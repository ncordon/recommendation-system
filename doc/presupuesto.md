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


  | Elementos    | Desglose | Coste inicial | Coste inicial por usuario | coste mensual fijo |  Coste mensual por usuario |
  |-----------------|--------------|--------------|--------------|-------------|-------------|
  | Servidor | - CPU: Quad-Core <br> - RAM: 8-16 GB <br> - HDD Online: 20 GB <br> - HDD Offline: 30 GB <br> - Refrigeración | 1431.67 € | 14.3167 - 28.6324 € | 119.3058 € | 1.193058 - 2.3861 |
  | Dominio | dominio .com (porkbun) | 8.84 € | 0.0884 - 0.1768 € | 0.7366 € | 0.01473 - 0.00736 €|
  | Luz | | 180 - 360 € | 2.7 - 5.4 € | 15 - 30 € | 0.225 - 0.45 € |
  | Mantenimiento |
  | Personal |
  | Total |

## Sistema basado en la nube

Estimación con AppEngine:

* 1 instancia por mes
  * 219 horas de cálculo CPU al mes (aprox 20 minutos cada hora).
  * Memoria usada: 91.25 GB al mes.
  * Disco usado: 30 GB al mes.
  * 300 MB de tráfico saliente al mes.
  * Almacenamiento cloud: 20 GB

Total: 44.20\$ al mes $\approx$ 41€ al mes.
