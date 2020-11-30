#pragma once

#include <stdint.h>

void init_sensor();
void read_sensor(int16_t *temp, uint16_t *humi);

