#include <BLEDevice.h>
#include <HardwareSerial.h>
#include <mbedtls/aes.h>
#include "uuid.h"

#define HEART_RATE_MAX_COUNT 45 // 5

#define CHG_EPS 0
#define CHG_HRT_RATE_CNT 1
#define EPS_CHG_STAGES 5 // 3
#define HRT_RATE_CHG_STAGES 9 // 3, 5, 7

int heartRateCount = HEART_RATE_MAX_COUNT;

int heartRateReadCount = 0;

bool sendOnSerial = true;

const std::string miBandBleAddress = "e2:b8:17:da:9a:0f";

static uint8_t	key [18] = {0x01, 0x08, 0x82, 0xb6, 0x5c, 0xd9, 0x91, 0x95, 0x9a, 0x72, 0xe5, 0xcc, 0xb7, 0xaf, 0x62, 0x33, 0xee, 0x35};
static uint8_t	encryptedNum[18] = {0x03, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
static uint8_t	sendRndCmd[2] = {0x02, 0x08};
static uint8_t	authKey[18];
static uint8_t	none[2] = {0x00, 0x00};

enum authenticationFlags {
  sendKey = 0,
	requireRandomNumber = 1,
	sendEncryptedNumber = 2,
	authFailed, authSuccess = 3,
	waiting = 4
};

enum dflag {
	error = -1,
	idle = 0,
	scanning = 1,
	connectingToDev = 2,
	connectingToServ = 3,
	established = 4,
	waitingForData = 5
};

authenticationFlags	 authFlag;
mbedtls_aes_context	aes;
dflag stat = idle;

static void notifyCallbackAuth(BLERemoteCharacteristic *pBLERemoteCharacteristic, uint8_t *pData, size_t len, bool isNotify) {
	switch (pData[1]) {
		case 0x01:
			if (pData[2] == 0x01) {
				authFlag = requireRandomNumber;
			}
			else {
				authFlag = authFailed;
			}
			break;
		case 0x02:
			if (pData[2] == 0x01) {
				mbedtls_aes_init(&aes);
				mbedtls_aes_setkey_enc(&aes, (authKey + 2), 128);
				mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_ENCRYPT, pData + 3, encryptedNum + 2);
				mbedtls_aes_free(&aes);
				authFlag = sendEncryptedNumber;
			} else {
				authFlag = authFailed;
			}
			break;
		case 0x03:
			if (pData[2] == 0x01) {
				authFlag = authSuccess;
			}
			else if (pData[2] == 0x04) {
				authFlag = sendKey;
			}
			break;
		default:
			authFlag = authFailed;
	}
}

static void notifyCallbackHeartRate(BLERemoteCharacteristic *pHRMMeasureCharacteristic, uint8_t *pData, size_t len, bool isNotify) {
  heartRateReadCount++;
  Serial.printf("Heart rate value %d = %d\n", heartRateReadCount, pData[1]);
  if (sendOnSerial) {
    Serial2.println(pData[1]);
  }
  stat = idle;
}

class DeviceSearcher: public BLEAdvertisedDeviceCallbacks {
public:
	void setDevAddr(std::string addr) {
		targetAddr = addr;
	}
	
	void onResult (BLEAdvertisedDevice advertisedDevice) {
		std::string addrNow = advertisedDevice.getAddress().toString();
		if (addrNow.compare(targetAddr) == 0) {
			pServerAddress = new BLEAddress(advertisedDevice.getAddress());
			found = true;
		}
	}
	
	bool isFound() {
		return found;
	}
	
	BLEAddress *getServAddr() {
		return pServerAddress;
	}
	
private:
	bool	 found = false;
	std::string	 targetAddr;
	BLEAddress	*pServerAddress;
};

class MiBand2 {
public:
	MiBand2(std::string addr, const uint8_t * key) {
		devAddr = addr;
		memcpy(authKey, key, 18);
	}
	
	~MiBand2() {
		pClient->disconnect();
		Serial.printf("MI Band 2 disconnected\n");
	}
	
	bool scanForDevice(uint8_t timeout) {
		DeviceSearcher *ds = new DeviceSearcher();
		ds->setDevAddr(devAddr);
		
		BLEScan* pBLEScan = BLEDevice::getScan();
		pBLEScan->setAdvertisedDeviceCallbacks(ds);
		pBLEScan->setActiveScan(true);
		pBLEScan->start(timeout);
		
		if (!ds->isFound()) {
			return false;
		} else {
			pServerAddress = ds->getServAddr();
			pClient = BLEDevice::createClient();
      pBLEScan->stop();
			return true;
		}
	}
	
	bool connectToServer(BLEAddress pAddress) {
		pClient->connect(pAddress, BLE_ADDR_TYPE_RANDOM);
    while (!pClient->isConnected()) {
      Serial.printf("Connection to MI Band 2 unsuccessful\n");
      pClient->connect(pAddress, BLE_ADDR_TYPE_RANDOM);
    }
    Serial.printf("Successfully connected to MI Band 2\n");
    delay(1000);

		BLERemoteService *pRemoteService = pClient->getService(SERVICE2_UUID);
		if (pRemoteService == nullptr) {
			return false;
    }
		pRemoteCharacteristic = pRemoteService->getCharacteristic(AUTH_CHARACTERISTIC_UUID);
		if (pRemoteCharacteristic == nullptr) {
			return false;
		}
    Serial.printf("Got CHAR_AUTH characteristic\n");
		
		pRemoteService = pClient->getService(ALERT_SEV_UUID);
    Serial.printf("Got SVC_ALERT service\n");
		pAlertCharacteristic = pRemoteService->getCharacteristic(ALERT_CHA_UUID);
    Serial.printf("Got CHAR_ALERT characteristic\n");
		
		pRemoteService = pClient->getService(HEART_RATE_SEV_UUID);
    Serial.printf("Got SVC_HEART_RATE service\n");
		pHRMControlCharacteristic = pRemoteService->getCharacteristic(UUID_CHAR_HRM_CONTROL);
    Serial.printf("Got UUID_CHAR_HRM_CONTROL characteristic\n");
		pHRMMeasureCharacteristic = pRemoteService->getCharacteristic(UUID_CHAR_HRM_MEASURE);
    Serial.printf("Got UUID_CHAR_HRM_MEASURE characteristic\n");
		cccdHrm = pHRMMeasureCharacteristic->getDescriptor(CCCD_UUID);
    Serial.printf("Got CCCD_HRM descriptor\n");
		connectd = true;

		pRemoteCharacteristic->registerForNotify(notifyCallbackAuth);
		pHRMMeasureCharacteristic->registerForNotify(notifyCallbackHeartRate);

		return true;
	}
	
	void authStart() {
    authFlag = sendKey;
		BLERemoteDescriptor *pAuthDescriptor;
		pAuthDescriptor = pRemoteCharacteristic->getDescriptor(CCCD_UUID);
		pAuthDescriptor->writeValue(HRM_NOTIFICATION, 2, true);
		Serial.printf("Sent {0x01, 0x00} to CCCD_AUTH, notifications enabled\n");
		while (authFlag != authSuccess) {
			Serial.printf("AUTH_FLAG = %d\n", authFlag);
			authenticationFlags savedFlag = authFlag;
			authFlag = waiting;
			switch (savedFlag) {
				case sendKey:
					pRemoteCharacteristic->writeValue(authKey, 18);
					Serial.printf("Sent auth key to CCCD_AUTH\n");
					break;
				case requireRandomNumber:
					pRemoteCharacteristic->writeValue(sendRndCmd, 2);
					Serial.printf("Sent random num request command to CCCD_AUTH\n");
					break;
				case sendEncryptedNumber:
					pRemoteCharacteristic->writeValue(encryptedNum, 18);
					Serial.printf("Sent encrypted num to CCCD_AUTH\n");
					break;
				default:
				;
			}
			if (authFlag == savedFlag) {
				authFlag = waiting;
			}
			delay(100);
		}
		pAuthDescriptor->writeValue(none, 2, true);
		Serial.printf("Sent null to CCCD_AUTH\n");
		while (!connectd && (authFlag == authSuccess));
    Serial.printf("Auth process successful\n");
		cccdHrm->writeValue(HRM_NOTIFICATION, 2, true);
    Serial.printf("Listening on the HRM_NOTIFICATION\n");
	}
	
	void startHrm() {
		Serial.printf("Sending HRM command\n");
		pHRMControlCharacteristic->writeValue(HRM_CONTINUOUS_STOP, 3, true);
		pHRMControlCharacteristic->writeValue(HRM_CONTINUOUS_START, 3, true);
		Serial.printf("Sent HRM command\n");
	}
	
	void startHrmOneShot() {
		if (stat != waitingForData) {
			Serial.printf("Sending HRM-OS command\n");
			pHRMControlCharacteristic->writeValue(HRM_ONESHOT_STOP, 3, true);
			pHRMControlCharacteristic->writeValue(HRM_ONESHOT_START, 3, true);
			Serial.printf("Sent HRM-OS command\n");
			stat = waitingForData;
		} else {
			delay(50);
		}
	}
	
	void init(uint8_t timeout) {
    Serial.printf("Device (MI Band 2) address - ");
    Serial.println(devAddr.c_str());
    Serial.printf("Scanning for device\n");
		if (!scanForDevice(timeout)) {
      Serial.printf("Device not found\n");
			return;
		}
    Serial.printf("Device found\n");
    Serial.printf("Connecting to services\n");
		if (!connectToServer(*pServerAddress)) {
      Serial.printf("Failed to connect to services\n");
			return;
		}
		authStart();
		stat = established;
	}
	
	void deinit() {
		pHRMControlCharacteristic->writeValue(HRM_CONTINUOUS_STOP, 3, true);
		pHRMControlCharacteristic->writeValue(HRM_ONESHOT_STOP, 3, true);
		pClient->disconnect();
    Serial.printf("Successfully disconnected from MI Band 2\n");
	}
	
private:
	bool	 found = false;
	bool	 connectd = false;

	std::string	 devAddr;
	BLEClient	*pClient;
	BLEAddress	*pServerAddress;
	BLERemoteCharacteristic	 *pRemoteCharacteristic;
	BLERemoteCharacteristic	 *pAlertCharacteristic;
	BLERemoteCharacteristic	 *pHRMMeasureCharacteristic;
	BLERemoteCharacteristic	 *pHRMControlCharacteristic;
	BLERemoteDescriptor	*cccdHrm;
};

bool readAndValidateHrmReqFromSerial() {
  // String str = Serial2.readStringUntil('\n');
  String str = "";
  char readByte;
  do {
    readByte = Serial2.read();
    if ((readByte >= 'a' && readByte <= 'z') || (readByte >= 'A' && readByte <= 'Z') || (readByte >= '0' && readByte <= '9')) {
     str += String(readByte);
    }
  } while (readByte != '\n');
  Serial.printf("Received HRM req\n");
  return str.equals("hrmReq");
}

MiBand2 miBand2(miBandBleAddress, key);

void setup() {
	Serial.begin(115200);
  Serial2.begin(9600);
  Serial.printf("One shot mode loading\n");
	BLEDevice::init("ESP-WROOM-32");
	miBand2.init(30);
}

void loop() {
#if CHG_EPS
  for (int i = 0; i < EPS_CHG_STAGES; i++) {
#elif CHG_HRT_RATE_CNT
  heartRateCount = 5;
  for (int i = 0; i < HRT_RATE_CHG_STAGES; i++) {
#endif
    Serial.printf("Waiting for HRM req\n");
    if (!readAndValidateHrmReqFromSerial()) {
      Serial.printf("Read/Validate for HRM req failed\n");
      sendOnSerial = false;
    }
    else {
      Serial.printf("Read and validate for HRM req succeeded\n");
    }
    for (int j = 0; j < heartRateCount; j++) {
      miBand2.startHrmOneShot();
      while (stat != idle) {
        delay(50);
      }
    }
    heartRateReadCount = 0;
#if CHG_HRT_RATE_CNT
    heartRateCount += 5;
#endif
    delay(50);
  }
  delay(50000);
	miBand2.deinit();
	delay(5000);
	esp_deep_sleep_start();
  exit(0); 
}
