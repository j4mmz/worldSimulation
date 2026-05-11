# WORLD SIMULATION: Simulacion Dinamica de Civilizaciones

## Descripcion
Este proyecto es un simulador parametrico que modela la evolución de cuatro continentes (Asia, Europa, América y África) a lo largo de varios ciclos. El motor combina modelos matemáticos de **demografía (Matrices de Leslie)**, **economía (Cobb-Douglas)**, **salud (Modelos SIR)** y **sociopolítica**, para otorgar el mayor realismo posible a la simulacion. 

## Como ejecutar el proyecto?
Para facilitar la ejecucion, el proyecto utiliza `uv`, un administrador de paquetes de Python, para instalar las librerias necesarias para que la simulacion funcione. Lo hace en un _venv_, por lo que no hay que preocuparse ed conflictos entre paquetes. Los siguientes pasos detallan como instalar `uv` y ejecutar la simulacion en los diferentes sistemas operativos

### Windows
En una terminal de **PowerShell**:
``` PowerShell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Reinicia la terminal cerrandola y abriendola. Despues, verifica que se ha instalado correctamente escribiendo el comando `uv --version`. Si devuelve la version significa que se ha instalado, sino visita la web oficial para mas info [https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1]

Una vez instalado, para ejecutar puedes hacer doble-click en el archivo `run.bat`, o ejecutar `.\run.bat` desde una terminal (estando en el mismo directorio del archivo)

### Linux/macOS
En una terminal, ejecutar el siguiente comando:
``` Bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
```
Al terminar, ejecuta `uv --version`. Si no funciona, ejecuta el comando `source $HOME/.cargo/env` para recargar la configuracion y prueba de nuevo. Para mas informacion visita la web oficial [https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1]

Una vez instalado, ejecuta `.\run.sh` en la terminal para correr la simulacion. Si da error por problemas de servicio utiliza `chmod +x run.sh` para darle permisos y prueba de nuevo

_Nota [10-5-2026]: aun falta por agregar eventos para que la simulacion sea mas realista, y no tan ideal. Acutalmente la poblacion crece sin problemas, junto con el resto de parametros (siempre que los parametros sean correctos)_
