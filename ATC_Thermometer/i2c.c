#include <stdint.h>
#include "tl_common.h"
#include "drivers.h"
#include "vendor/common/user_config.h"
#include "app_config.h"
#include "drivers/8258/gpio_8258.h"

RAM bool i2c_sending;

void init_i2c(){
	i2c_gpio_set(I2C_GPIO_GROUP_C2C3); 
	i2c_master_init(0x78, (uint8_t)(CLOCK_SYS_CLOCK_HZ/(4*600000)) );
}

void send_i2c(uint8_t device_id, uint8_t *buffer, int dataLen){
	if(i2c_sending)return;
	i2c_sending=true;
	i2c_set_id(device_id);
	i2c_write_series(0, 0, (uint8_t*)buffer,dataLen);
	i2c_sending=false;
}

uint8_t test_i2c_device(uint8_t address){	
	reg_i2c_id = address<<1;
	reg_i2c_ctrl = FLD_I2C_CMD_START | FLD_I2C_CMD_ID;
	while(reg_i2c_status & FLD_I2C_CMD_BUSY);
	reg_i2c_ctrl = FLD_I2C_CMD_STOP;
	while(reg_i2c_status & FLD_I2C_CMD_BUSY	);
	
return (reg_i2c_status & FLD_I2C_NAK)?0:1;
}
