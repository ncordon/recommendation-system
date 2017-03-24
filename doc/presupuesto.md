---
author:
- Lothar Soto Palma
- Daniel López García
- Ignacio Cordón Castillo

title: "Presupuesto del sistema de recomendación de música"
lang: spanish
date: \today
papersize: A4
geometry: left=4cm, right=2cm

# Especifica que queremos un índice
toc-title: "Índice de contenidos"
toc: true
toc-depth: 2

# Paquetes a usar en la compilación de latex
header-includes:
  - \usepackage{graphicx}
  - \usepackage{verbatim}
---

\newcommand{\imgn}[2]{
  \begin{center}
    \includegraphics[width=#1\textwidth]{#2}
  \end{center}
}

\newpage

# Presupuesto
El presupuesto se basa principalmente en el diagrama de despliegue. Asumiendo que el proyecto recibe el visto bueno y suponiendo que el sistema será capaz de atender al menos a 50-100 usuarios concurrentes en su inicio podemos definir los siguientes presupuestos:

## Sistema "in House"

  * Hardware necesario:
    * Servidor (hosting):
      * CPU: Quad-Core
      * RAM: 8-16 GB
      * HDD Online: 20 GB
      * HDD Offline: 30 GB
      * Refrigeración
  * Software necesario:
    * Sistema servidor Linux (p.e. CentOS)
    * Python y librerías.
    * Dominio.
  * Servicios:
    * Luz.
  * Personal/Mantenimiento.

  |              |                                           |                           |                                            |                   |                                    |
  |--------------|-------------------------------------------|---------------------------|--------------------------------------------|-------------------|------------------------------------|
  |    Elementos    |    Desglose                                  | Coste inicial (€) (anual) | Coste inicial por usuario (€/pers) (anual) | Coste mensual (€) | Coste mensual por usuario (€/pers) | 
  | Servidor     | CPU: Quad-Core                            | 308,99                    | 0,154495                                   | 25,74916       | 0,012874                        |
  |              | RAM: 8-16 GB                              | 173,98                    | 0,08699                                    | 14,49833       | 0,007249                        |
  |              | HDD Online: 1 TB                          | 84                        | 0,042                                      | 7                 | 0,0035                             |
  |              | HDD OffLine 1 TB                          | 84                        | 0,084                                      | 7                 | 0,007                              |
  |              | Refrigeración                             | 141,11                    | 0,070555                                   | 11,75916       | 0,005879                        |
  |              | Otros elementos(cables, placa, cajas,...) | 599,92                    | 0,29996                                    | 49,9933      | 0,02499                        |
  | Dominio      | Nombre de dominio                         | 8,84                      | 0,00442                                    | 0,73666     | 0,00036                        |
  | Luz          | Fuente 500-600W                           | 630,14184                 | 0,315070                                 | 52,51182          | 0,02625                         |
  | Servicio Red | Conexión a internet (ADSL) 300Mb - 1Gb    | 65,4                      | 0,0327                                     | 5,45              | 0,002725                           |
  |              | IP fija                                   | 300                       | 0,15                                       | 25                | 0,0125                             |
  | Réplica      |                                           | 1400,84                   | 0,70042                                    | 116,7366       | 0,058368                      |
  | Total        |                                           | 3797,22184                | 1,94061                                 | 316,43515       | 0,161717                        |



## Sistema basado en la nube

Estimación con AppEngine:

* 1 instancia por mes
  * 219 horas de cálculo CPU al mes (aprox 20 minutos cada hora).
  * Memoria usada: 91.25 GB al mes.
  * Disco usado: 30 GB al mes.
  * 300 MB de tráfico saliente al mes.
  * Almacenamiento cloud: 20 GB

Total: 44.20\$ al mes $\approx$ 41€ al mes.
