# S3 Storage Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   FastAPI    │  │   Lambda     │  │   Frontend   │                  │
│  │  Endpoints   │  │  Functions   │  │  React App   │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
│         │                  │                  │                          │
│         └──────────────────┴──────────────────┘                          │
│                            │                                              │
└────────────────────────────┼──────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────┐        ┌─────────────────────────┐         │
│  │   data_service.py       │        │   model_service.py      │         │
│  ├─────────────────────────┤        ├─────────────────────────┤         │
│  │ • load_climate_data()   │        │ • load_risk_model()     │         │
│  │ • load_health_data()    │        │ • load_forecast_model() │         │
│  │ • load_locations()      │        │ • load_scaler()         │         │
│  │ • save_predictions()    │        │ • save_model()          │         │
│  │ • save_forecasts()      │        │ • list_models()         │         │
│  │ • get_storage_stats()   │        │ • model_exists()        │         │
│  └────────────┬────────────┘        └────────────┬────────────┘         │
│               │                                   │                       │
│               └───────────────┬───────────────────┘                       │
│                               │                                           │
└───────────────────────────────┼───────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         UTILITY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                     s3_storage.py                                  │  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  CSV Operations          JSON Operations       Model Operations   │  │
│  │  ├─ save_csv_to_s3()    ├─ save_json_to_s3()  ├─ save_model()    │  │
│  │  └─ load_csv_from_s3()  └─ load_json_from_s3()└─ load_model()    │  │
│  │                                                                     │  │
│  │  File Operations         Utility Operations                        │  │
│  │  ├─ upload_file()        ├─ list_objects()                        │  │
│  │  └─ download_file()      ├─ object_exists()                       │  │
│  │                          ├─ delete_object()                        │  │
│  │                          └─ get_bucket_size()                      │  │
│  └────────────────────────────────┬──────────────────────────────────┘  │
│                                   │                                      │
└───────────────────────────────────┼──────────────────────────────────────┘
                                    │
                                    │ boto3
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS S3 STORAGE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐ │
│  │   Raw Data Bucket   │  │ Processed Data      │  │  Models Bucket  │ │
│  │                     │  │     Bucket          │  │                 │ │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────┤ │
│  │ raw/                │  │ processed/          │  │ models/         │ │
│  │ ├─ climate_data.csv │  │ ├─ climate_*.csv    │  │ ├─ risk.pkl     │ │
│  │ ├─ health_data.csv  │  │ ├─ health_*.csv     │  │ ├─ forecast.pkl │ │
│  │ ├─ hospital_data.csv│  │ └─ ...              │  │ └─ scaler.joblib│ │
│  │ └─ locations.csv    │  │                     │  │                 │ │
│  │                     │  │ predictions/        │  │                 │ │
│  │                     │  │ ├─ 2024-11-11/      │  │                 │ │
│  │                     │  │ └─ ...              │  │                 │ │
│  │                     │  │                     │  │                 │ │
│  │                     │  │ forecasts/          │  │                 │ │
│  │                     │  │ alerts/             │  │                 │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────┘ │
│                                                                           │
│  Region: us-east-1       Region: us-east-1       Region: us-east-1      │
└─────────────────────────────────────────────────────────────────────────┘


DATA FLOW EXAMPLES:
═══════════════════

1. Loading Climate Data:
   ┌─────────────┐
   │ FastAPI     │
   │ Endpoint    │
   └──────┬──────┘
          │ request_data(location='KA')
          ▼
   ┌─────────────┐
   │ data_service│
   │.load_climate│
   │  _data()    │
   └──────┬──────┘
          │ load_csv_from_s3('raw/climate_data.csv')
          ▼
   ┌─────────────┐
   │ s3_storage  │
   │.load_csv()  │
   └──────┬──────┘
          │ boto3.get_object()
          ▼
   ┌─────────────┐
   │   AWS S3    │
   │ Raw Bucket  │
   └─────────────┘


2. Making Predictions:
   ┌─────────────┐
   │ Lambda      │
   │ Function    │
   └──────┬──────┘
          │ 1. load_model()
          ▼
   ┌─────────────┐
   │model_service│
   │.load_risk() │
   └──────┬──────┘
          │ 2. boto3.get_object()
          ▼
   ┌─────────────┐
   │   AWS S3    │
   │Models Bucket│
   └─────────────┘
          │
          │ 3. model returned
          ▼
   ┌─────────────┐
   │ Lambda      │
   │ predict()   │
   └──────┬──────┘
          │ 4. save_predictions()
          ▼
   ┌─────────────┐
   │data_service │
   │.save_pred() │
   └──────┬──────┘
          │ 5. save_json_to_s3()
          ▼
   ┌─────────────┐
   │   AWS S3    │
   │Process. Bkt │
   └─────────────┘


3. Batch Processing:
   ┌──────────────┐
   │   Glue Job   │
   └──────┬───────┘
          │ 1. Read raw data
          ▼
   ┌──────────────┐      ┌──────────────┐
   │   AWS S3     │──────▶│   Process    │
   │  Raw Data    │      │     Data     │
   └──────────────┘      └──────┬───────┘
                                │ 2. Write processed
                                ▼
                         ┌──────────────┐
                         │   AWS S3     │
                         │  Processed   │
                         └──────────────┘


MIGRATION WORKFLOW:
══════════════════

   Local Storage                    S3 Storage
   ─────────────                    ──────────

   data/raw/              ───────▶  s3://raw-bucket/raw/
   ├─ climate_data.csv    migration ├─ climate_data.csv
   ├─ health_data.csv     ───────▶  ├─ health_data.csv
   └─ ...                           └─ ...

   data/processed/        ───────▶  s3://processed-bucket/processed/
   ├─ file1.csv          migration  ├─ file1.csv
   └─ ...                ───────▶   └─ ...

   models/                ───────▶  s3://models-bucket/models/
   ├─ risk_model.pkl     migration  ├─ risk_model.pkl
   └─ ...                ───────▶   └─ ...

   [migrate_data_to_s3.py executes the migration]


BENEFITS:
════════

✅ Scalability      - No local disk space limits
✅ Durability       - 99.999999999% durability (11 9's)
✅ Availability     - Access from anywhere
✅ Collaboration    - Multiple users/services
✅ Cost-Effective   - Pay only for what you use
✅ Integration      - Works with Lambda, SageMaker, Glue
✅ Versioning       - Optional version control
✅ Lifecycle        - Automatic archival to Glacier
```
