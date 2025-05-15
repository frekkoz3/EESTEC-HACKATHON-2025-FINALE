/**
 * Torque control example of adaptive gripper. Based on SimpleFOC library.
 *
 * 1. After flashing this code to the XMC4700 Relax Kit, angle alignment will be
 *    applied. The gripper must be opened to its fullest extent to release the gear
 *    and minimize load for alignment.
 *
 * 2. After angle alignment, attach the gears (manually close the gripper a bit
 *    to align the gears) and you can start controlling the gripper's opening and
 *    closing. Pressing button 1 on the board will close the gripper, and pressing
 *    button 2 will open it. Note: There is no upper limit set for opening, so it
 *    is possible that the gears may detach if the maximum is exceeded.
 *
 * 3. Open the serial monitor/serial plotter to view data from the magnetic
 *    sensors placed under the TPU material on top of the clip. When the gripping
 *    clip grabs an object and generates pressure, the data changes.
 *
 * This is a basic example; you can be creative to improve this gripper!
 */
#include "TLE5012Sensor.h"
#include "TLx493D_inc.hpp"
#include "config.h"
#include <SimpleFOC.h>
#include <stdlib.h>
#include <stdio.h>

using namespace std;

// define SPI pins for TLE5012 sensor
#define PIN_SPI1_SS0 94  // Chip Select (CS) pin
#define PIN_SPI1_MOSI 69 // MOSI pin
#define PIN_SPI1_MISO 95 // MISO pin
#define PIN_SPI1_SCK 68  // SCK pin

static float last_x = 0, last_y = 0, last_z = 0;
static bool start = false;            // This is used to understand how to actually begin
static bool detecting = false;        // This is used to detect when it is gripping an object
static bool profiling = false;        // This is used to detect what type of object we are gripping
static bool holding = false;          // This is used to detect when we are gonna hold the object
static bool releasing = false;        // This is used to detect when its time to release the object
static int detecting_count = 0;       // This is the counter of step used for detection
static int max_detecting_count = 5;   // This is the maximum value for the counter for detection
static int profiling_count = 0;       // This is the counter of step used for profiling
static int max_profiling_count = 30;  // This is the maximum value for the counter for profiling
static bool release_request = false;  // This is used to detect when we want the gripper to release the object its holding
static String profile_type = "";      // This is the type of profile detected
static int step = 0;                  // This is a simple step counter 
static int max_step = 20;             // This is the period for the step counter
static int releasing_time = 0;        // This is the counter for the release action

// create an instance of SPIClass3W for 3-wire SPI communication
tle5012::SPIClass3W tle5012::SPI3W1(2);

// create an instance of TLE5012Sensor
TLE5012Sensor tle5012Sensor(&SPI3W1, PIN_SPI1_SS0, PIN_SPI1_MISO, PIN_SPI1_MOSI,
                            PIN_SPI1_SCK);

// BLDC motor instance BLDCMotor (polepairs, motor phase resistance, motor KV
// rating, motor phase inductance)
BLDCMotor motor = BLDCMotor(
    7, 0.24, 360,
    0.000133); // 7 pole pairs, 0.24 Ohm phase resistance, 360 KV and 0.000133H
// you can find more data of motor in the doc

// define driver pins
const int U = 11;
const int V = 10;
const int W = 9;
const int EN_U = 6;
const int EN_V = 5;
const int EN_W = 3;

// BLDC driver instance
BLDCDriver3PWM driver = BLDCDriver3PWM(U, V, W, EN_U, EN_V, EN_W);

// voltage set point variable
float target_voltage = -1;

#if ENABLE_MAGNETIC_SENSOR
// create a instance of 3D magnetic sensor
using namespace ifx::tlx493d;
TLx493D_A2B6 dut(Wire1, TLx493D_IIC_ADDR_A0_e);
// define the number of calibration samples
const int CALIBRATION_SAMPLES = 20;
// offsets for calibration
double xOffset = 0, yOffset = 0, zOffset = 0;
#endif

#if ENABLE_COMMANDER
// instantiate the commander
Commander command = Commander(Serial);
void doTarget(char *cmd) { command.scalar(&target_voltage, cmd); }
#endif

void setup() {
  // use monitoring with serial
  Serial.begin(115200);
  // enable more verbose output for debugging
  // comment out if not needed
  SimpleFOCDebug::enable(&Serial);

  // initialise magnetic sensor hardware
  tle5012Sensor.init();
  // link the motor to the sensor
  motor.linkSensor(&tle5012Sensor);

  // power supply voltage
  driver.voltage_power_supply = 12;
  // limit the maximal dc voltage the driver can set
  // as a protection measure for the low-resistance motors
  // this value is fixed on startup
  driver.voltage_limit = 6;
  if (!driver.init()) {
    Serial.println("Driver init failed!");
    return;
  }
  // link the motor and the driver
  motor.linkDriver(&driver);

  // aligning voltage
  motor.voltage_sensor_align = 2;
  // choose FOC modulation (optional)
  motor.foc_modulation = FOCModulationType::SpaceVectorPWM;
  // set motion control loop to be used
  motor.controller = MotionControlType::torque;

  // comment out if not needed
  // motor.useMonitoring(Serial);

  // initialize motor
  motor.init();
  // align sensor and start FOC
  motor.initFOC();
  Serial.println(F("Motor ready."));

#if ENABLE_MAGNETIC_SENSOR
  // start 3D magnetic sensor
  dut.begin();
  // calibrate 3D magnetic sensor to get the offsets
  calibrateSensor();
  Serial.println("3D magnetic sensor Calibration completed.");

  // set the pin modes for buttons
  pinMode(BUTTON1, INPUT);
  pinMode(BUTTON2, INPUT);
#endif

  Serial.print("setup done.\n");
#if ENABLE_COMMANDER
  // add target command T
  command.add('T', doTarget, "target voltage");
  Serial.println(F("Set the target voltage using serial terminal:"));
#endif
  _delay(20);
}

void loop() {
  step = step++%max_step;
#if ENABLE_MAGNETIC_SENSOR
  // BUTTON 1 USED FOR STARTING THE PROCEDURE
  if (digitalRead(BUTTON1) == LOW){
    Serial.print("Starting!\n");
    start = true;
    delay(300); // PRESSING A BUTTON GENERATE PROBLEM
  }
  // BUTTON 2 USED FOR RESETTING THE PROCEDURE
  if (digitalRead(BUTTON2) == LOW){
    reset_state();
    delay(300);
  }
  /*
  if (start && !detecting && !profiling && !holding){
    Serial.print("Time to swing around\n");
  }*/

  // DETECTING PHASE
  if (!detecting && start){
    target_voltage = -2;
  }else if (detecting && start){
    target_voltage = -1;
  }else if(profiling){
    target_voltage = -0.5;
  }
  else if (releasing){
    target_voltage = 0.1*releasing_time;
    releasing_time ++;
    if (releasing_time == 20){
      Serial.print("Restarting\n");
      reset_state();
    }
  }

  // read the magnetic field data
  double x, y, z;
  dut.setSensitivity(TLx493D_FULL_RANGE_e);
  dut.getMagneticField(&x, &y, &z);

  // subtract the offsets from the raw data
  x -= xOffset;
  y -= yOffset;
  z -= zOffset;

  //plotter(x, y, z);

  float dx = x - last_x;
  float dy = y - last_y;
  float dz = z - last_z;

  float dmagnitude = sqrt(dx*dx + dy*dy + dz*dz);

  if(dmagnitude > 0.45 && !detecting && start && !profiling && !holding && !releasing){
    detecting = true;
    detecting_count = 0;
    Serial.print("Detecting\n");
  }

  // DETECTING PHASE
  String detected_validity = "";
  if (detecting){
    print_data(dmagnitude, x, y, z);
    detecting_count ++;
    if (detecting_count == max_detecting_count){
      Serial.print("Checking\n");
      bool read = false;
      while (!read){
        if (Serial.available()>0){
          detected_validity = Serial.readStringUntil('\n');
          detected_validity.trim();
          read = true;
          if (detected_validity == "D"){
            detecting = false;
            profiling = true;
            Serial.print("Profiling\n");
            profiling_count = 0;
          }
          if (detected_validity == "N"){
            Serial.print("False Detection occurred\n");
            detecting = false;
          }
        }
      }
    }
  }

  // PROFILING PHASE
  if (profiling){
    print_data(dmagnitude, x, y, z);
    profiling_count ++;
    if (profiling_count == max_profiling_count){
      profiling = false;
      Serial.print("Checking\n");
      holding = true;
      bool read = false;
      while(!read){
        if (Serial.available()>0) {
          profile_type = Serial.readStringUntil('\n');
          profile_type.trim();
          read = true;
        }
      }
      Serial.print("Holding\n");
    }
  }

  // HOLDING PHASE
  // Here we have to set a specific voltage profile
  if(holding){
    if (profile_type == "H"){
      target_voltage = -3;
    }
    else if (profile_type == "M"){
      target_voltage = step < max_step/2 ? -0.5 : -1.5 ;
    }
    else if (profile_type == "S"){
      target_voltage = step < max_step/2 ? -0.5 : 0.2;
    }
    if (dmagnitude > 0.45){
      holding = false;
      releasing = true;
      Serial.print("Releasing\n");
    }
  }

  last_x = x;
  last_y = y;
  last_z = z;
  
#endif
  // update angle sensor data
  tle5012Sensor.update();
#if ENABLE_READ_ANGLE
  float angle = tle5012Sensor.getSensorAngle();
  if(profiling){
    Serial.print("\n");
    Serial.print(angle);
    Serial.print(", ");
  }
#endif
  // main FOC algorithm function
  // the faster you run this function the better
  // Arduino UNO loop  ~1kHz
  // Bluepill loop ~10kHz
  motor.loopFOC();

  // Motion control function
  // velocity, position or voltage (defined in motor.controller)
  // this function can be run at much lower frequency than loopFOC() function
  // You can also use motor.move() and set the motor.target in the code
  motor.move(target_voltage);
  
#if ENABLE_COMMANDER
  // user communication
  command.run();
#endif
}

#if ENABLE_MAGNETIC_SENSOR
/**
 * @brief Calibrates the magnetic field sensor by calculating the average
 * offsets for the X, Y, and Z axes over a series of samples.
 */
void calibrateSensor() {
  double sumX = 0, sumY = 0, sumZ = 0;

  for (int i = 0; i < CALIBRATION_SAMPLES; ++i) {
    double temp;
    double valX, valY, valZ;

    dut.getMagneticFieldAndTemperature(&valX, &valY, &valZ, &temp);
    sumX += valX;
    sumY += valY;
    sumZ += valZ;

    delay(10); // Adjust delay as needed
  }

  // Calculate average offsets
  xOffset = sumX / CALIBRATION_SAMPLES;
  yOffset = sumY / CALIBRATION_SAMPLES;
  zOffset = sumZ / CALIBRATION_SAMPLES;
}
#endif

// function to reset
void reset_state(){
  // pls open the hand UwU
  last_x = 0, last_y = 0, last_z = 0;
  start = false;
  detecting = false;
  profiling = false;
  holding = false;
  releasing = false;
  detecting_count = 0;
  profiling_count = 0;
  release_request = false;
  profile_type = "";
  step = 0;
  releasing_time = 0;   
}

void print_data(double dmagnitude, double x, double y, double z){
  Serial.print(dmagnitude);
  Serial.print(",");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(z);
  Serial.print("\n");
}

void plotter(double x, double y, double z){
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(z);
  Serial.print("\n");
}
