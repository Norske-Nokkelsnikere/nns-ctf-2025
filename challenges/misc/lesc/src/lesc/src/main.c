#include <zephyr/kernel.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/services/bas.h>

#include <zephyr/settings/settings.h>

#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(MAIN, LOG_LEVEL_DBG);

static const struct bt_data ad[] = { BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)), BT_DATA(BT_DATA_NAME_COMPLETE, CONFIG_BT_DEVICE_NAME, sizeof(CONFIG_BT_DEVICE_NAME))};

static void connected(struct bt_conn* conn, uint8_t err)
{
    if (err)
    {
        LOG_INF("Connection failed (err 0x%02x)", err);
    }
    else
    {
        LOG_INF("Connected");
    }
}

static void disconnected(struct bt_conn* conn, uint8_t reason)
{
    LOG_INF("Disconnected (reason 0x%02x)", reason);
}

static void security_changed(struct bt_conn* conn, bt_security_t level, enum bt_security_err err)
{
    char addr[BT_ADDR_LE_STR_LEN];

    bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));

    if (!err)
    {
        LOG_INF("Security changed: %s level %u\n", addr, level);
    }
    else
    {
        LOG_ERR("Security failed: %s level %u err %d\n", addr, level, err);
    }
}


BT_CONN_CB_DEFINE(conn_callbacks) = { .connected = connected, .disconnected = disconnected, .security_changed = security_changed };

static void auth_passkey_display(struct bt_conn* conn, unsigned int passkey)
{
    char addr[BT_ADDR_LE_STR_LEN];

    bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));

    LOG_INF("Passkey for %s: %06u", addr, passkey);
}

static void auth_cancel(struct bt_conn* conn)
{
    char addr[BT_ADDR_LE_STR_LEN];

    bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));

    LOG_INF("Pairing cancelled: %s", addr);
}


static struct bt_conn_auth_cb auth_cb_display = {
    .passkey_display = auth_passkey_display,
    .passkey_entry = NULL,
    .cancel = auth_cancel,
};

int main(void)
{
    LOG_INF("Loaded flag as %s", (const char*)(0x35d8));

    int err = bt_enable(NULL);
    if (err)
    {
        LOG_ERR("Failed to enable Bluetooth: %d", err);
        return err;
    }

    if (IS_ENABLED(CONFIG_SETTINGS))
    {
        settings_load();
    }

    err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
    if (err)
    {
        LOG_ERR("Failed to start advertising: %d", err);
        return err;
    }

    err = bt_conn_auth_cb_register(&auth_cb_display);
    if (err)
    {
        LOG_ERR("Failed to register auth callbacks: %d", err);
        return err;
    }

    

    LOG_INF("Started Bluetooth advertising");

}
