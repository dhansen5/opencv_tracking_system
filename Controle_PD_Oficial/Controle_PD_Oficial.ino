
// Bibliotecas utilizadas
#include <Servo.h>
#include <TimerThree.h>

// Constantes do Controlador PD sem filtro derivativo
volatile double KpX = 0.4;  
volatile double KpY = 0.4;
volatile double Td = 0.1;

// Declaração da constante de tempo de amostragem
volatile double ts = 0.02;

// Declaração das variáveis do sinal de controle
volatile double uX;
volatile double uY;

// Declaração das variáveis de erro
volatile double erroX;
volatile double erroX_ant = 0;

volatile double erroY;
volatile double erroY_ant = 0;


// Inicialização dos servos
volatile double servoXSpeed = 1485; // ServoX fica parado (Teoricamente 1500 = parado, porém depende da regulagem do rest point.)
volatile double servoYSpeed = 1500; // ServoY fica parado

Servo servoX; // Servo Horizontal
Servo servoY; // Servo Horizontal

// Inicialização do algoritmo
void setup() {
  Serial.begin(115200);                   // Habilita comunicação Serial

  servoX.attach(9);                       // Pino para o PWM do servo horizontal
  servoY.attach(12);                      // Pino para o PWM do servo vertical
  servoX.writeMicroseconds(servoXSpeed);  // Ordena o servoX ficar parado
  servoY.writeMicroseconds(servoYSpeed);  // Ordena o servoY ficar parado

  Timer3.initialize(ts*1000000);          // Tempo de amostragem da interrupção
  Timer3.attachInterrupt(controlePD);     // Nomeia a interrupção de tempo

}

// Recebimento dos valores de erro
void loop() {
  
      if(Serial.available() > 0)
  {
    if(Serial.read() == 'X')
    {
      erroX = Serial.parseInt();
      if(Serial.read() == 'Y')
      {
        erroY = Serial.parseInt();
      }
    }
  }
}

// Interrupção de tempo / Algoritmo de controle
void controlePD(){

  // Escalonamento de ganhos
  if(erroX > 100 || erroX < -100) KpX = 0.67;
  else if (erroX > 150 || erroX < -150) KpX = 1;
  else KpX = 0.4;

  if(erroY > 100 || erroY < -100) KpY = 0.67;
  else if (erroY > 150 || erroY < -150) KpY = 1;
  else KpY = 0.4;

  // Cálculo dos sinais de controle
  uX  = 1/ts*((KpX*Td + KpX*ts)*erroX - KpX*Td*erroX_ant);
  uY  = 1/ts*((KpY*Td + KpY*ts)*erroY - KpY*Td*erroY_ant);
      
  // Saturação do sinal de controle
//    if (uX > 100) {
//      uX = 100;
//    }
//  
//    if (uX < -100) {
//      uX = -100;
//    }
//  
//    if (uY > 100) {
//      uY = 100;
//    }
//    if (uY < -100) {
//      uY = -100;
//    }

  // Envio do sinal PWM
  servoXSpeed = 1485 + uX;
  servoYSpeed = 1500 - uY;
      
  servoX.writeMicroseconds(servoXSpeed);
  servoY.writeMicroseconds(servoYSpeed);

  // Atualização das variáveis utilizadas para o controle
  erroX_ant = erroX;
  erroY_ant = erroY;
      
  }

  
