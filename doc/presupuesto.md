---
author:
- Lothar Soto Palma
- Daniel López García
- Ignacio Cordón Castillo

title: "Presupuesto del sistema de recomendación de música"
lang: spanish
date: \today
papersize: A4
geometry: landscape, left=4cm, right=2cm

# Especifica que queremos un índice
toc-title: "Índice de contenidos"
toc: false
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



El presupuesto se basa principalmente en el diagrama de despliegue. Asumimos que el proyecto recibe el visto bueno y que el sistema será capaz de atender al menos a 50-100 usuarios concurrentes,
y a un número total de usuarios de 2000.

# Sistema "in House"

  * Hardware necesario:
    * Servidor (hosting):
      * CPU: Quad-Core
      * RAM: 8-16 GB
      * HDD Online: 20 GB
      * HDD Offline: 30 GB
      * Refrigeración
  * Software necesario:
    * Sistema servidor Linux (p.e. CentOS, Ubuntu)
    * Python y librerías.
  * Dominio.
  * Servicios:
    * Luz.
    * Personal/Mantenimiento.

  | Elementos    | Desglose                                  | Inicial anual(€) | Inicial anual (€/usuario) | Mensual (€)  | Mensual (€/usuario) | 
  |--------------|-------------------------------------------|------------------|---------------------------|--------------|---------------------|
  | Servidor     | CPU: Quad-Core                            | 308,99           | 0,154495                  | 25,74916     | 0,012874            |
  |              | RAM: 8-16 GB                              | 173,98           | 0,08699                   | 14,49833     | 0,007249            |
  |              | HDD Online: 1 TB                          | 84               | 0,042                     | 7            | 0,0035              |
  |              | HDD OffLine 1 TB                          | 84               | 0,084                     | 7            | 0,007               |
  |              | Refrigeración                             | 141,11           | 0,070555                  | 11,75916     | 0,005879            |
  |              | Otros elementos(cables, placa, cajas,...) | 599,92           | 0,29996                   | 49,9933      | 0,02499             |
  | Dominio      | Nombre de dominio                         | 8,84             | 0,00442                   | 0,73666      | 0,00036             |
  | Luz          | Fuente 500-600W                           | 630,14184        | 0,315070                  | 52,51182     | 0,02625             |
  | Servicio Red | Conexión a internet (ADSL) 300Mb - 1Gb    | 65,4             | 0,0327                    | 5,45         | 0,002725            |
  |              | IP fija                                   | 300              | 0,15                      | 25           | 0,0125              |
  | Réplica      |                                           | 1400,84          | 0,70042                   | 116,7366     | 0,058368            |
  | **Total**    |                                           | **3797,23**      | **1,95**                  | **316,44**   | **0,17**            |



\newpage

# Sistema basado en la nube

Estimación hecha con AppEngine, desde [App Engine Pricing Calculator](https://cloud.google.com/products/calculator/#tab=app-engine)

Aparte de la infraestructura propocionada por App Engine se precisa, como en el caso del sistema "in house":

 * Softrare: 
    * Sistema servidor Linux (p.e. CentOS, Ubuntu)
    * Python y librerías.
  * Dominio.
 

  | Elementos    | Desglose                                  | Inicial anual(€) | Inicial anual (€/usuario) | Mensual (€)  | Mensual (€/usuario) |
  |--------------|-------------------------------------------|------------------|---------------------------|--------------|---------------------|
  | Dominio      | Nombre de dominio                         | 8,84             | 0,00442                   | 0,73666      | 0,00036             |
  | App Engine   | 1 instancia mensual                       |                  |                           |              |                     |
  |              | 220 horas de cálculo al mes(20 min/hora)  |                  |                           |              |                     |
  |              | 30 GB de disco mensuales                  |                  |                           |              |                     |
  |              | 91 GB de memoria mensuales                |                  |                           |              |                     |
  |              | 300 MB de tráfico saliente por mes        |                  |                           |              |                     |
  |              | Almacenamiento cloud de 20 GB             | 492              | 0,246                     | 41           | 0,0205              |
  | **Total**    |                                           | **500,84**       | **0,26**                  | **41,74**    | **0,03**            |
