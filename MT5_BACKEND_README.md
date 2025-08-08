# MT5 Integration Backend Overview

This document provides an overview of how the MT5 integration backend works, including its server-side logic and database structure.

## Overview
The MT5 integration backend is designed to manage and execute Expert Advisors (EAs) on MetaTrader 5 accounts. It provides APIs for starting, stopping, pausing, and resuming algorithms, as well as risk management features.

## Key Components

### 1. **Server-Side Logic**
- **APIs**: The backend exposes RESTful APIs for managing EAs.
  - `start_algorithm`: Starts an EA on a specified MT5 account.
  - `stop_algorithm`: Stops a running EA.
  - `pause_algorithm`: Pauses a running EA.
  - `resume_algorithm`: Resumes a paused EA.
- **Risk Management**: The `RiskManager` class calculates and monitors trading risks dynamically based on the MT5 account setup.
- **Subprocess Management**: EAs are executed as subprocesses, and their process IDs (PIDs) are tracked in the database.

### 2. **Database Structure**
- **AlgorithmExecution**: Tracks the execution status of EAs, including their PIDs, start/stop times, and performance metrics.
- **MT5Account**: Stores information about the user's MT5 account, such as login credentials and allowed symbols.

## Workflow
1. **Starting an Algorithm**:
   - The `start_algorithm` API is called with the algorithm name and symbol.
   - The backend validates the user's MT5 account and starts the EA as a subprocess.
   - The `AlgorithmExecution` table is updated with the execution details.

2. **Risk Management**:
   - The `RiskManager` class calculates the current risk based on open positions and account balance.
   - Risk details are included in the API response.

3. **Stopping/Pausing/Resuming an Algorithm**:
   - The respective API is called with the execution ID.
   - The backend retrieves the PID from the `AlgorithmExecution` table and manages the subprocess accordingly.

## How to Use
1. **Setup**:
   - Ensure the backend is running and connected to the MT5 terminal.
   - Configure the `MT5Account` with valid credentials.

2. **API Endpoints**:
   - Use the provided endpoints to manage EAs.
   - Example request body for `start_algorithm`:
     ```json
     {
       "algorithm_name": "mt5_candy_ea",
       "symbol": "EURUSD"
     }
     ```

3. **Monitoring**:
   - Check the `AlgorithmExecution` table for the status of running EAs.
   - Use the risk management details in the API response to monitor trading risks.

## Notes
- Ensure the MT5 terminal is running and accessible by the backend.
- The `RiskManager` class relies on accurate account and position data from the MT5 API.
- Logs are generated for debugging and monitoring purposes.

For more details, refer to the source code and API documentation.
