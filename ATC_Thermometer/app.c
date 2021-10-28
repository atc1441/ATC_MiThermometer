#include <stdint.h>
#include "tl_common.h"
#include "drivers.h"
#include "stack/ble/ble.h"
#include "vendor/common/blt_common.h"

#include "battery.h"
#include "ble.h"
#include "flash.h"
#include "lcd.h"
#include "sensor.h"



RAM uint32_t last_delay = 0xFFFF0000, last_adv_delay = 0xFFFF0000, last_battery_delay = 0xFFFF0000;
RAM bool last_smiley;
int16_t temp = 0;
uint16_t humi = 0;
RAM uint8_t adv_count = 0;
RAM uint8_t meas_count = 254;
RAM int16_t last_temp;
RAM uint16_t last_humi;
RAM uint8_t battery_level;
RAM uint16_t battery_mv;
RAM bool show_batt_or_humi;

//Settings
extern settings_struct settings;

RAM int16_t comfort_x[] = {2000, 2560, 2700, 2500, 2050, 1700, 1600, 1750};
RAM uint16_t comfort_y[] = {2000, 1980, 3200, 6000, 8200, 8600, 7700, 3800};

_attribute_ram_code_ bool is_comfort(int16_t t, uint16_t h) {
    bool c = 0;
    uint8_t npol = sizeof(comfort_x) / sizeof(comfort_x[0]);
    for (uint8_t i = 0, j = npol - 1; i < npol; j = i++)
    {
      if ((
        (comfort_y[i] < comfort_y[j]) && (comfort_y[i] < h) && (h <= comfort_y[j]) &&
        ((comfort_y[j] - comfort_y[i]) * (t - comfort_x[i]) > (comfort_x[j] - comfort_x[i]) * (h - comfort_y[i]))
      ) || (
        (comfort_y[i] > comfort_y[j]) && (comfort_y[j] < h) && (h <= comfort_y[i]) &&
        ((comfort_y[j] - comfort_y[i]) * (t - comfort_x[i]) < (comfort_x[j] - comfort_x[i]) * (h - comfort_y[i]))
      ))
        c = !c;
    }
    return c;
}

void user_init_normal(void){//this will get executed one time after power up
	random_generator_init();  //must
	init_ble();	
	init_sensor();
	init_lcd();	
	init_flash();
	show_atc_mac();
	battery_mv = get_battery_mv();
	battery_level = get_battery_level(get_battery_mv());
}

_attribute_ram_code_ void user_init_deepRetn(void){//after sleep this will get executed
	init_lcd_deepsleep();
	blc_ll_initBasicMCU();
	rf_set_power_level_index (RF_POWER_P3p01dBm);
	blc_ll_recoverDeepRetention();
}

void main_loop(){	
	if((clock_time()-last_delay) > 5000*CLOCK_SYS_CLOCK_1MS){//main loop delay
	
		if((clock_time()-last_battery_delay) > 5*60000*CLOCK_SYS_CLOCK_1MS){//Read battery delay
			battery_mv = get_battery_mv();
			battery_level = get_battery_level(get_battery_mv());
			last_battery_delay = clock_time();
		}

		if(meas_count >= settings.measure_interval){
			read_sensor(&temp,&humi);		
			temp += settings.temp_offset;
			humi += settings.humi_offset;
			meas_count=0;
		
			if((temp-last_temp > settings.temp_alarm_point)||(last_temp-temp > settings.temp_alarm_point)||(humi-last_humi > settings.humi_alarm_point)||(last_humi-humi > settings.humi_alarm_point)){// instant advertise on to much sensor difference
				if(settings.advertising_temp_C_or_F)
					set_adv_data(((((temp*10)/5)*9)+3200)/10, humi, battery_level, battery_mv);
				else
					set_adv_data(temp, humi, battery_level, battery_mv);
			}
			last_temp = temp;
			last_humi = humi;
		}	
		meas_count++;
		
		if(settings.temp_C_or_F){
			show_temp_symbol(2);
			show_big_number(((((last_temp*10)/5)*9)+3200)/10,1);//convert C to F
		}else{
			show_temp_symbol(1);
			show_big_number(last_temp,1);
		}

		if(!settings.show_batt_enabled) show_batt_or_humi = true;
		
		if(show_batt_or_humi){//Change between Humidity displaying and battery level if show_batt_enabled=true
			show_small_number(last_humi,1);	
		    show_battery_symbol(0);   
		}else{
			show_small_number((battery_level==100)?99:battery_level,1);
			show_battery_symbol(1);
		}
		
		show_batt_or_humi = !show_batt_or_humi;
		
		if(ble_get_connected()){//If connected notify Sensor data
			ble_send_temp(last_temp);
			ble_send_humi(last_humi);
			ble_send_battery(battery_level);
		}

		if((clock_time() - last_adv_delay) > (settings.advertising_type?5000:10000)*CLOCK_SYS_CLOCK_1MS){//Advetise data delay
		    if(adv_count >= settings.advertising_interval){
				if(settings.advertising_temp_C_or_F)
					set_adv_data(((((last_temp*10)/5)*9)+3200)/10, last_humi, battery_level, battery_mv);
				else
					set_adv_data(last_temp, last_humi, battery_level, battery_mv);
			last_adv_delay = clock_time();
			adv_count=0;
		    }
		    adv_count++;
		}
		
		if(settings.comfort_smiley) {
			if(is_comfort(last_temp * 10, last_humi * 100)){
				show_smiley(1);
			} else {
				show_smiley(2);
			}
		}

		if(settings.blinking_smiley){//If Smiley should blink do it
		last_smiley=!last_smiley;
		show_smiley(last_smiley);
		}
		
		update_lcd();
		last_delay = clock_time();
	}
	blt_sdk_main_loop();
	blt_pm_proc();	
}
