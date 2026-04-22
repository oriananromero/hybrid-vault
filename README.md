# 🚀 Hybrid Vault: Cifrado Híbrido y Monitorización Blue Team

## 🛡️ Descripción del Proyecto
Este proyecto combina el desarrollo de una herramienta de criptografía híbrida (AES-256 + RSA) en Python con técnicas de monitorización y análisis defensivo en entornos Linux. El objetivo es simular un escenario de protección de datos (o una técnica de Ransomware) y demostrar cómo detectar estos artefactos en un SOC (Security Operations Center).

## 🛠️ Tecnologías Utilizadas
- **Lenguaje**: Python 3.x (Librería cryptography).
- **Criptografía**: AES-128 (Fernet) para datos, RSA-2048 para intercambio de llaves.
- **Defensa/SOC**: ``Auditd`` (Linux Auditing System), ``Wireshark`` (Análisis de tráfico), ``Hexdump``.

## Fases del Proyecto
1. **Implementación del Cifrado Híbrido**
   Explico cómo implementé la lógica donde se genera una llave simétrica aleatoria para los datos y se protege mediante cifrado asimétrico.
   - **Confidencialidad**: Protección de archivos mediante estándares industriales, solo quien tenga la llave privada RSA puede obtener la llave AES para leer el archivo.
   - **Seguridad en Reposo**: La llave privada RSA se almacena cifrada mediante una contraseña (AES-BestAvailableEncryption). Si roban la PC, no se puede utilizar la llave.

2. **Detección y Análisis (Enfoque Blue Team)**
   Esta es la parte central de mi perfil como Analista de Seguridad. He analizado el "rastro" que deja la herramienta en el sistema:
   
   A. **Análisis Binario (Entropy Analysis)**
   Utilizando ``hexdump``, identifiqué la diferencia entre un archivo de texto plano y el artefacto cifrado (``vault.file``).
       **Observación**: El archivo cifrado presenta alta cantidad de datos ilegibles y carece de cadenas de texto legibles, un indicador clave de compromiso (IoC) en ataques de exfiltración.

   B. **Monitorización con Auditd**
   Configuré reglas de auditoría en el núcleo de Linux para detectar la creación de llaves y archivos cifrados.
   - **Regla**: ``sudo auditctl -w /home/oriana/hybrid-vault -p wa -k alert_vault``
   - **Resultado**: Identificación del proceso exacto, el usuario y los archivos afectados (``.pem``, ``vault.file``).

   C. **Simulación de Exfiltración (Análisis de Red)**
   Simulé el envío de los datos cifrados a un servidor externo mediante Netcat y analicé el tráfico con Wireshark.
   - **Hallazgo**: Identificación de flujos de datos cifrados por puertos no estándar (4444), técnica común en la fase de exfiltración de un ciberataque.
  
## 📈 Conclusiones para un SOC
Este proyecto me permitió entender: 
  1. Cómo los atacantes (Ransomware) utilizan el cifrado para denegar el acceso a los datos.
  2. Cómo identificar artefactos criptográficos en un análisis forense rápido.
  3. La importancia de tener reglas de auditoría configuradas para detectar procesos no autorizados manipulando archivos sensibles.

## Imagenes de prueba 
 - Ejecución del Proceso
   <img width="806" height="181" alt="code_process" src="https://github.com/user-attachments/assets/2375de17-a8b3-46fb-9299-e97cc6cac415" />
   *Flujo completo de la herramienta: generación de llaves RSA de 2048 bits, cifrado del archivo objetivo y posterior recuperación exitosa mediante la llave privada.*
   
- Contraste de Entropía
  <img width="796" height="116" alt="msg_codigo" src="https://github.com/user-attachments/assets/b21c391a-103b-455b-b1cc-b4c7c8215a66" />
  *En el original: Se lee perfectamente el texto.*
  
  <img width="968" height="516" alt="ciphered_file" src="https://github.com/user-attachments/assets/ad985745-652a-4ed2-a13f-2a31f769ee51" />
  *En el cifrado: Es puro ruido. En la línea 00000100 se ve perfectamente el separador ---SEPARATOR---.*

  *Detección mediante análisis de archivos (File Analysis). Mientras el original es legible, el artefacto vault.file muestra una estructura de alta ilegibilidad. La presencia del separador en texto plano dentro del binario   es un indicador que permite identificar la estructura del payload durante una investigación forense.*

- Monitorización del Sistema
  <img width="1853" height="879" alt="auditctl-capture" src="https://github.com/user-attachments/assets/6235bed1-34ff-44b7-9abe-572cdac92955" />
  *Implementación de telemetría mediante Auditd. El log captura el momento exacto en que el intérprete de Python interactúa con archivos sensibles. Como analista, este rastro permite la atribución: sé exactamente qué         proceso y qué usuario generaron las llaves criptográficas. Incluso si el atacante borra el script después de ejecutarlo, el log de auditd ya ha registrado que /usr/bin/python3.12 fue el ejecutor, dándome una pista          forense imborrable*
  
- Análisis de Tráfico y Exfiltración
  <img width="1594" height="843" alt="wireshark_traffic" src="https://github.com/user-attachments/assets/0980c43d-81c7-49c6-85db-252c972ed62d" />

  <img width="1227" height="145" alt="trash_payload" src="https://github.com/user-attachments/assets/2ee088f7-0601-409c-bb9b-5c12f50a7552" />

  *Simulación de exfiltración de datos. En Wireshark se identifica una conexión TCP hacia el puerto 4444 (puerto no estándar). Al seguir el flujo TCP (Follow Stream), se confirma que el contenido no sigue ningún protocolo     conocido y transporta datos cifrados, lo que activaría una alerta de seguridad por sospecha de robo de información.*



## Instalación y prueba
``pip install cryptography`` => para esta prueba, he creado un entorno privado venv, este comando fue ejecutado dentro de la carpeta del proyecto en el entorno venv.
``sudo apt install auditd `` => se realiza la instalación en el núcleo de linux.

