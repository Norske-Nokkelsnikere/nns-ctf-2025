#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/gatt.h>
#include <stddef.h>
#include <string.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(FLAG, LOG_LEVEL_DBG);

static struct bt_uuid_128 flag_store_service_uuid = BT_UUID_INIT_128(0x8d, 0xc9, 0x65, 0x16, 0x53, 0xe7, 0x72, 0x93, 0x5, 0x2a, 0x17, 0x24, 0x00, 0x14, 0x00, 0x00);
static struct bt_uuid_128 flag_characteristic_uuid = BT_UUID_INIT_128(0x8d, 0xc9, 0x65, 0x16, 0x53, 0xe7, 0x72, 0x93, 0x5, 0x2a, 0x17, 0x24, 0x01, 0x14, 0x00, 0x00);

static ssize_t flag_read(struct bt_conn* conn, const struct bt_gatt_attr* attr, void* buf, uint16_t len, uint16_t offset);

// Flag is stored in main core
const char* flag = (const char*)(0x35d8);


BT_GATT_SERVICE_DEFINE(flag_store_service, BT_GATT_PRIMARY_SERVICE(&flag_store_service_uuid),
                       BT_GATT_CHARACTERISTIC(&flag_characteristic_uuid.uuid, BT_GATT_CHRC_READ, BT_GATT_PERM_READ_AUTHEN | BT_GATT_PERM_READ_LESC, flag_read, NULL, NULL)
);

static ssize_t flag_read(struct bt_conn* conn, const struct bt_gatt_attr* attr, void* buf, uint16_t len, uint16_t offset)
{
    return bt_gatt_attr_read(conn, attr, buf, len, offset, flag, strlen(flag));
}