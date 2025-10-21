#include <zephyr/kernel.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/drivers/gpio.h>
#include "dsp.h"

#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(MAIN, LOG_LEVEL_DBG);

static const struct adc_dt_spec adc_channel = ADC_DT_SPEC_GET(DT_PATH(zephyr_user));
static const struct gpio_dt_spec flag_led = GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);

int main(void)
{
    if (!adc_is_ready_dt(&adc_channel)) {
        LOG_ERR("ADC controller devivce %s not ready", adc_channel.dev->name);
	    return -1;
    }

    int err = adc_channel_setup_dt(&adc_channel);
    if (err < 0) {
        LOG_ERR("Could not setup channel #%d (%d)", 0, err);
        return -1;
    }

    err = gpio_pin_configure_dt(&flag_led, GPIO_OUTPUT);
    if (err < 0) {
        LOG_ERR("Failed to init flag detection pin (%d)", err);
        return -1;
    }
	

    for (;;) {
        uint16_t flag_buffer[28];

        for (int i = 0; i < ARRAY_SIZE(flag_buffer); i++)
        {
            struct adc_sequence sequence = {
                .buffer = flag_buffer + i,
                /* buffer size in bytes, not number of samples */
                .buffer_size = sizeof(flag_buffer[0]),
                //Optional
                //.calibrate = true,
            };

            err = adc_read(adc_channel.dev, &sequence);
            if (err < 0) {
                LOG_ERR("Could not read (%d)", err);
                continue;
            }
        }

        bool flag = is_flag(flag_buffer, ARRAY_SIZE(flag_buffer));

        if (flag) {
            gpio_pin_set_dt(&flag_led, true);
        }
    }
}
