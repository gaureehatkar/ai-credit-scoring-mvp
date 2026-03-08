# Requirements Document: AI-Powered Credit Scoring MVP Platform

## Introduction

This document specifies the functional and non-functional requirements for an AI-powered credit scoring platform targeting unbanked and underbanked populations. The platform uses machine learning to evaluate creditworthiness based on alternative data sources, providing financial inclusion for individuals and MSMEs lacking traditional credit histories. The system consists of a FastAPI backend, React/TypeScript frontend, PostgreSQL database, and pre-trained ML models with SHAP explainability.

## Glossary

- **System**: The AI-Powered Credit Scoring MVP Platform
- **Backend**: The FastAPI application server
- **Frontend**: The React/TypeScript web application
- **Database**: The PostgreSQL database instance
- **ML_Model**: The pre-trained XGBoost credit scoring model
- **SHAP_Explainer**: The SHAP (SHapley Additive exPlanations) model explainability component
- **User**: A registered person using the system (applicant or admin)
- **Applicant**: A user with the "applicant" role who submits credit applications
- **Admin**: A user with the "admin" role who manages applications
- **Application**: A credit application submitted by an applicant
- **Credit_Score**: A numerical score between 300-850 indicating creditworthiness
- **JWT_Token**: JSON Web Token used for authentication
- **Alternative_Data**: Non-traditional credit data (remittances, utility bills, gig platform metrics, etc.)
- **Risk_Category**: Classification of credit risk as "low", "medium", or "high"
- **SHAP_Explanation**: Feature importance explanation for a credit score prediction
- **Default_Probability**: The probability (0-1) that an applicant will default on a loan
- **Feature_Vector**: A set of engineered numerical features used for ML prediction
- **Application_Status**: The current state of an application ("pending", "approved", "rejected", "under_review")

## Requirements

### Requirement 1: User Registration and Authentication

**User Story:** As a new user, I want to register an account with email and password, so that I can access the credit scoring platform.

#### Acceptance Criteria

1. WHEN a user submits valid registration data, THE System SHALL create a new user account with a hashed password
2. WHEN a user submits registration data with an existing email, THE System SHALL reject the registration and return an error message
3. WHEN a user registers, THE System SHALL hash the password using bcrypt with cost factor 12
4. WHEN a user provides a password shorter than 8 characters, THE System SHALL reject the registration
5. WHEN a user successfully registers, THE System SHALL generate a JWT_Token valid for 24 hours
6. WHEN a user logs in with valid credentials, THE System SHALL return a JWT_Token containing user_id, email, and role
7. WHEN a user logs in with invalid credentials, THE System SHALL return HTTP 401 Unauthorized without revealing whether the email exists
8. WHEN a JWT_Token expires, THE System SHALL reject API requests with HTTP 401 Unauthorized

### Requirement 2: Credit Application Submission

**User Story:** As an applicant, I want to submit a credit application with my personal and alternative data, so that I can receive a credit score.

#### Acceptance Criteria

1. WHEN an authenticated applicant submits a valid credit application, THE System SHALL create an application record in the Database
2. WHEN an applicant submits an application with age less than 18, THE System SHALL reject the application with HTTP 422 Unprocessable Entity
3. WHEN an applicant submits an application with requested_amount less than or equal to 0, THE System SHALL reject the application
4. WHEN an applicant submits an application with fewer than 3 alternative data fields, THE System SHALL reject the application
5. WHEN an application is created, THE System SHALL set the initial status to "pending"
6. WHEN an application is submitted, THE System SHALL trigger credit score prediction within 2 seconds
7. WHEN an applicant submits more than 3 applications within 30 days, THE System SHALL reject the submission with HTTP 429 Too Many Requests
8. WHEN an application is successfully created, THE System SHALL return HTTP 201 Created with the application_id

### Requirement 3: Credit Score Prediction

**User Story:** As an applicant, I want the system to calculate my credit score using machine learning, so that I can understand my creditworthiness.

#### Acceptance Criteria

1. WHEN an application is submitted, THE Prediction_Service SHALL engineer at least 10 numeric features from the application data
2. WHEN features are engineered, THE Prediction_Service SHALL ensure no NaN or infinite values exist in the Feature_Vector
3. WHEN the ML_Model predicts a credit score, THE System SHALL ensure the score is between 300 and 850
4. WHEN the ML_Model generates a default probability, THE System SHALL ensure the probability is between 0 and 1
5. WHEN a Credit_Score is calculated, THE System SHALL assign a Risk_Category based on the score value
6. WHEN the Credit_Score is 700 or above, THE System SHALL assign Risk_Category as "low"
7. WHEN the Credit_Score is between 600 and 699 inclusive, THE System SHALL assign Risk_Category as "medium"
8. WHEN the Credit_Score is below 600, THE System SHALL assign Risk_Category as "high"
9. WHEN a Credit_Score is generated, THE System SHALL store it in the Database with a one-to-one relationship to the Application
10. WHEN the ML_Model completes prediction, THE System SHALL complete the entire prediction process within 100 milliseconds

### Requirement 4: Feature Engineering

**User Story:** As the system, I want to engineer features from raw application data, so that the ML model can make accurate predictions.

#### Acceptance Criteria

1. WHEN application data is received, THE Prediction_Service SHALL extract basic demographic features including age and requested_amount
2. WHEN application data contains missing alternative data fields, THE Prediction_Service SHALL impute missing numeric values with 0
3. WHEN the applicant_type is "unbanked", THE Prediction_Service SHALL extract remittance_frequency, community_verification_score, and microfinance_repayment_count
4. WHEN the applicant_type is "underbanked", THE Prediction_Service SHALL extract gig_platform_rating, upi_transaction_frequency, and savings_account_balance
5. WHEN features are engineered, THE Prediction_Service SHALL create derived features including age_squared and log_requested_amount
6. WHEN numeric features exceed the range [-10, 10], THE Prediction_Service SHALL clip them to this range
7. WHEN feature engineering completes, THE Prediction_Service SHALL return a Feature_Vector with feature_names sorted alphabetically
8. WHEN monthly_income is greater than 0, THE Prediction_Service SHALL calculate debt_to_income_ratio as requested_amount divided by annual income

### Requirement 5: SHAP Explainability

**User Story:** As an applicant, I want to understand which factors influenced my credit score, so that I can improve my creditworthiness.

#### Acceptance Criteria

1. WHEN a Credit_Score is generated, THE SHAP_Explainer SHALL compute SHAP values for all features in the Feature_Vector
2. WHEN SHAP values are computed, THE System SHALL select the top 10 features by absolute SHAP value
3. WHEN a SHAP_Explanation is created, THE System SHALL include feature_name, feature_value, shap_value, and impact
4. WHEN a shap_value is positive, THE System SHALL set impact to "positive"
5. WHEN a shap_value is negative or zero, THE System SHALL set impact to "negative"
6. WHEN SHAP explanations are generated, THE System SHALL sort them by absolute SHAP value in descending order
7. WHEN the SHAP_Explainer fails, THE System SHALL log a warning and return the Credit_Score with an empty explanations list
8. WHEN SHAP explanations are stored, THE System SHALL persist them as JSON in the Database

### Requirement 6: Application Status Management

**User Story:** As the system, I want to automatically update application status based on credit score, so that applicants receive timely decisions.

#### Acceptance Criteria

1. WHEN a Credit_Score of 700 or above is generated, THE System SHALL update the Application_Status to "approved"
2. WHEN a Credit_Score between 600 and 699 is generated, THE System SHALL update the Application_Status to "under_review"
3. WHEN a Credit_Score below 600 is generated, THE System SHALL update the Application_Status to "rejected"
4. WHEN an Admin updates an Application_Status, THE System SHALL validate the new status is one of: "pending", "approved", "rejected", "under_review"
5. WHEN an Application_Status is updated, THE System SHALL update the updated_at timestamp
6. WHEN the ML_Model prediction fails, THE System SHALL set the Application_Status to "under_review" instead of failing the request

### Requirement 7: Application Retrieval and Authorization

**User Story:** As an applicant, I want to view my credit applications and scores, so that I can track my application history.

#### Acceptance Criteria

1. WHEN an authenticated Applicant requests their applications, THE System SHALL return only applications where user_id matches the authenticated user
2. WHEN an Applicant requests a specific application by ID, THE System SHALL verify the application belongs to the authenticated user
3. WHEN an Applicant attempts to access another user's application, THE System SHALL return HTTP 403 Forbidden
4. WHEN an application is retrieved, THE System SHALL include the associated Credit_Score if it exists
5. WHEN an application is retrieved, THE System SHALL mask the phone_number to show only the last 4 digits
6. WHEN an Applicant requests their application list, THE System SHALL support pagination with skip and limit parameters
7. WHEN no skip parameter is provided, THE System SHALL default to 0
8. WHEN no limit parameter is provided, THE System SHALL default to 100

### Requirement 8: Admin Application Management

**User Story:** As an admin, I want to view all applications and update their status, so that I can manage the credit approval process.

#### Acceptance Criteria

1. WHEN an authenticated Admin requests all applications, THE System SHALL return applications from all users
2. WHEN an Admin requests applications with a status filter, THE System SHALL return only applications matching that status
3. WHEN an Admin updates an Application_Status, THE System SHALL persist the change to the Database
4. WHEN an Admin requests platform statistics, THE System SHALL return total_applications, approved, rejected, under_review, and average_credit_score
5. WHEN a non-Admin user attempts to access admin endpoints, THE System SHALL return HTTP 403 Forbidden
6. WHEN an Admin views applications, THE System SHALL include full phone_number without masking

### Requirement 9: JWT Token Management

**User Story:** As the system, I want to securely manage authentication tokens, so that only authorized users can access protected resources.

#### Acceptance Criteria

1. WHEN a JWT_Token is generated, THE System SHALL sign it with the HS256 algorithm using the SECRET_KEY
2. WHEN a JWT_Token is generated, THE System SHALL set the expiration time to 24 hours from creation
3. WHEN a JWT_Token is generated, THE System SHALL include user_id, email, and role in the payload
4. WHEN a protected endpoint receives a request, THE System SHALL validate the JWT_Token before processing
5. WHEN a JWT_Token signature is invalid, THE System SHALL return HTTP 401 Unauthorized
6. WHEN a JWT_Token is expired, THE System SHALL return HTTP 401 Unauthorized
7. WHEN a JWT_Token is valid, THE System SHALL extract the user information from the payload

### Requirement 10: Database Schema and Relationships

**User Story:** As the system, I want to maintain data integrity through proper database schema design, so that data remains consistent and reliable.

#### Acceptance Criteria

1. THE Database SHALL enforce a unique constraint on the User email field
2. THE Database SHALL enforce a foreign key relationship between Application.user_id and User.id
3. THE Database SHALL enforce a unique constraint on CreditScore.application_id
4. THE Database SHALL maintain a one-to-one relationship between Application and CreditScore
5. WHEN a User is deleted, THE Database SHALL cascade delete all associated Applications
6. THE Database SHALL create indexes on User.email, Application.user_id, and Application.created_at
7. THE Database SHALL store Alternative_Data as JSON in the Application table
8. THE Database SHALL store SHAP_Explanations as JSON in the CreditScore table

### Requirement 11: Input Validation

**User Story:** As the system, I want to validate all input data, so that invalid data does not corrupt the database or cause errors.

#### Acceptance Criteria

1. WHEN a user submits data, THE System SHALL validate email format using Pydantic EmailStr validator
2. WHEN a user submits an age value, THE System SHALL ensure it is between 18 and 100 inclusive
3. WHEN a user submits a requested_amount, THE System SHALL ensure it is greater than 0
4. WHEN alternative data contains gig_platform_rating, THE System SHALL ensure it is between 0 and 5
5. WHEN alternative data contains community_verification_score, THE System SHALL ensure it is between 0 and 10
6. WHEN alternative data contains numeric fields, THE System SHALL ensure they are non-negative where specified
7. WHEN validation fails, THE System SHALL return HTTP 422 Unprocessable Entity with specific field errors
8. WHEN a request payload exceeds 1MB, THE System SHALL reject the request

### Requirement 12: Error Handling and Recovery

**User Story:** As a user, I want the system to handle errors gracefully, so that I receive helpful error messages and the system remains stable.

#### Acceptance Criteria

1. WHEN the Database connection fails, THE System SHALL return HTTP 503 Service Unavailable
2. WHEN the ML_Model fails to load, THE System SHALL log the error and return HTTP 500 Internal Server Error
3. WHEN the ML_Model prediction fails, THE System SHALL set Application_Status to "under_review" and log the error
4. WHEN feature engineering produces invalid values, THE System SHALL clip values to valid ranges and log a warning
5. WHEN an application is not found, THE System SHALL return HTTP 404 Not Found
6. WHEN authentication fails, THE System SHALL return HTTP 401 Unauthorized without revealing whether the email exists
7. WHEN authorization fails, THE System SHALL return HTTP 403 Forbidden
8. WHEN the SHAP_Explainer fails, THE System SHALL return the Credit_Score with empty explanations and log a warning

### Requirement 13: Rate Limiting

**User Story:** As the system, I want to limit the number of applications per user, so that the system is not abused and resources are fairly distributed.

#### Acceptance Criteria

1. WHEN an Applicant has submitted 3 applications within 30 days, THE System SHALL reject additional applications
2. WHEN an application is rejected due to rate limiting, THE System SHALL return HTTP 429 Too Many Requests
3. WHEN a rate limit error is returned, THE System SHALL include a retry_after value in seconds
4. WHEN 30 days have passed since the oldest application, THE System SHALL allow new applications
5. WHERE rate limiting is implemented, THE System SHALL count only applications created by the authenticated user

### Requirement 14: Security and Data Protection

**User Story:** As a user, I want my personal and financial data to be secure, so that my information is protected from unauthorized access.

#### Acceptance Criteria

1. THE System SHALL never store passwords in plain text
2. WHEN a password is stored, THE System SHALL hash it using bcrypt with cost factor 12
3. THE System SHALL never log passwords, JWT tokens, or other sensitive credentials
4. WHEN API responses include phone numbers for non-Admin users, THE System SHALL mask all but the last 4 digits
5. THE System SHALL use parameterized queries through SQLAlchemy ORM to prevent SQL injection
6. WHERE CORS is configured, THE System SHALL allow only the configured frontend origin
7. THE System SHALL validate and sanitize all string inputs to prevent XSS attacks
8. THE System SHALL store the SECRET_KEY in environment variables, never in source code

### Requirement 15: ML Model Performance

**User Story:** As a system administrator, I want the ML model to meet performance benchmarks, so that credit scores are accurate and reliable.

#### Acceptance Criteria

1. THE ML_Model SHALL achieve an AUC-ROC score of at least 0.79 on the test dataset
2. WHEN the ML_Model is trained, THE System SHALL use the Give Me Some Credit dataset
3. WHEN the ML_Model makes a prediction, THE System SHALL complete inference within 100 milliseconds
4. THE ML_Model SHALL use XGBoost as the gradient boosting algorithm
5. WHEN the ML_Model is loaded at startup, THE System SHALL verify the model file integrity
6. THE System SHALL log the model_version with each Credit_Score for traceability
7. WHEN the ML_Model is trained, THE System SHALL handle class imbalance using scale_pos_weight

### Requirement 16: API Response Time

**User Story:** As a user, I want the system to respond quickly, so that I have a smooth experience.

#### Acceptance Criteria

1. WHEN an Applicant submits a credit application, THE System SHALL respond within 2 seconds at the 95th percentile
2. WHEN a User authenticates, THE System SHALL respond within 500 milliseconds at the 95th percentile
3. WHEN a User retrieves their application list, THE System SHALL respond within 1 second at the 95th percentile
4. WHEN an Admin loads the dashboard, THE System SHALL respond within 3 seconds at the 95th percentile
5. WHEN the ML_Model performs inference, THE System SHALL complete within 100 milliseconds

### Requirement 17: Data Persistence and Consistency

**User Story:** As the system, I want to ensure data is persisted reliably, so that no data is lost during failures.

#### Acceptance Criteria

1. WHEN an Application is created, THE System SHALL commit the database transaction before returning a response
2. WHEN a Credit_Score is generated, THE System SHALL store it in the Database within the same transaction as the Application status update
3. WHEN a database transaction fails, THE System SHALL rollback all changes and return an error
4. WHEN an Application is created, THE System SHALL set created_at and updated_at timestamps
5. WHEN an Application is updated, THE System SHALL update the updated_at timestamp
6. THE Database SHALL maintain referential integrity through foreign key constraints

### Requirement 18: Model Loading and Initialization

**User Story:** As the system, I want to load the ML model efficiently at startup, so that predictions are fast and memory is used effectively.

#### Acceptance Criteria

1. WHEN the Backend starts, THE System SHALL load the ML_Model from disk once
2. WHEN the Backend starts, THE System SHALL load the SHAP_Explainer from disk once
3. WHEN the Backend starts, THE System SHALL load feature_names from disk once
4. THE System SHALL keep the ML_Model in memory for the lifetime of the application
5. THE System SHALL keep the SHAP_Explainer in memory for the lifetime of the application
6. WHEN model loading fails, THE System SHALL log the error and prevent the application from starting
7. WHEN the ML_Model is loaded, THE System SHALL verify the model file exists at the configured MODEL_PATH

### Requirement 19: Health Check and Monitoring

**User Story:** As a system administrator, I want to monitor system health, so that I can detect and resolve issues quickly.

#### Acceptance Criteria

1. THE System SHALL provide a /health endpoint that does not require authentication
2. WHEN the /health endpoint is called, THE System SHALL return the application status, version, database connection status, and model loading status
3. WHEN the Database is unreachable, THE /health endpoint SHALL report database status as "disconnected"
4. WHEN the ML_Model is not loaded, THE /health endpoint SHALL report model status as "not_loaded"
5. WHEN all components are healthy, THE /health endpoint SHALL return HTTP 200 OK
6. WHEN any component is unhealthy, THE /health endpoint SHALL return HTTP 503 Service Unavailable

### Requirement 20: Deployment and Configuration

**User Story:** As a developer, I want to deploy the system using Docker Compose, so that setup is simple and reproducible.

#### Acceptance Criteria

1. THE System SHALL provide a docker-compose.yml file that defines all services
2. WHEN Docker Compose is started, THE System SHALL start the Database, Backend, and Frontend services
3. WHEN the Database service starts, THE System SHALL run health checks before marking it as ready
4. WHEN the Backend service starts, THE System SHALL wait for the Database to be healthy
5. WHEN the Backend service starts, THE System SHALL run Alembic migrations automatically
6. THE System SHALL read configuration from environment variables defined in a .env file
7. THE System SHALL provide a .env.example file with all required configuration variables
8. WHEN the Frontend service starts, THE System SHALL configure the API URL from the VITE_API_URL environment variable

## Non-Functional Requirements

### Requirement 21: Scalability

**User Story:** As a system administrator, I want the system to handle the expected load, so that users have a reliable experience.

#### Acceptance Criteria

1. THE System SHALL support at least 10-20 concurrent users
2. THE System SHALL handle at least 100-200 applications per day
3. THE System SHALL handle at least 1000-2000 API requests per day
4. THE Database connection pool SHALL maintain 5-20 connections
5. WHEN the system is deployed, THE System SHALL require minimum 2 CPU cores and 4GB RAM

### Requirement 22: Maintainability and Code Quality

**User Story:** As a developer, I want the codebase to be well-tested and maintainable, so that I can add features and fix bugs efficiently.

#### Acceptance Criteria

1. THE System SHALL achieve at least 85% test coverage for all service modules
2. THE System SHALL include unit tests for all service classes
3. THE System SHALL include integration tests for all API endpoints
4. THE System SHALL include property-based tests for feature engineering and credit score calculation
5. THE System SHALL use type hints throughout the Python codebase
6. THE System SHALL use TypeScript for the Frontend to ensure type safety
7. THE System SHALL follow PEP 8 style guidelines for Python code
8. THE System SHALL use Pydantic models for all API request and response schemas

### Requirement 23: Logging and Auditing

**User Story:** As a system administrator, I want comprehensive logging, so that I can troubleshoot issues and maintain audit trails.

#### Acceptance Criteria

1. THE System SHALL log all authentication attempts with timestamp, email, and success/failure status
2. THE System SHALL log all credit score access with user_id, application_id, and timestamp
3. THE System SHALL log all Application_Status changes with admin_id and timestamp
4. THE System SHALL log all ML_Model prediction errors with full stack traces
5. THE System SHALL log all Database connection errors
6. THE System SHALL retain logs for at least 90 days
7. THE System SHALL never log passwords, JWT tokens, or other sensitive credentials

### Requirement 24: Data Retention and Compliance

**User Story:** As a compliance officer, I want the system to follow data retention policies, so that we comply with financial regulations.

#### Acceptance Criteria

1. THE System SHALL store Application records for at least 7 years
2. THE System SHALL provide a mechanism for users to request data deletion (GDPR compliance)
3. THE System SHALL anonymize data after the retention period expires
4. THE System SHALL maintain audit logs for all data access and modifications
5. THE System SHALL document all features used in the ML_Model to ensure fair lending compliance

### Requirement 25: Backup and Recovery

**User Story:** As a system administrator, I want regular database backups, so that data can be recovered in case of failure.

#### Acceptance Criteria

1. THE System SHALL perform daily database backups
2. WHEN a backup is created, THE System SHALL verify the backup file integrity
3. THE System SHALL retain database backups for at least 30 days
4. THE System SHALL provide a mechanism to restore from backup
5. WHEN the Database fails, THE System SHALL support recovery from the most recent backup

