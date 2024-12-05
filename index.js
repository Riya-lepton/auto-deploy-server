module.exports = {
  NODE_ENV: process.env.NODE_ENV,
  GMAP_API_KEY: process.env.GMAP_API_KEY,
  PORT: process.env.LAC_RAC_TAC_SERVICE_PORT ,
  DB_TYPE: process.env.NOSQL_DB_TYPE,
  // DB_TYPE: process.env.SQL_DB_TYPE,
  LOGGER_SERVICE_PATH: process.env.LOGGER_SERVICE_PATH,
  RO_IMAGE_PATH : process.env.RO_IMAGE_PATH,
  TICKET_IMAGE_PATH : process.env.TICKET_IMAGE_PATH,
  SQL_DB_TYPE: process.env.SQL_DB_TYPE,
  DB_TYPES: JSON.parse(process.env.DB_TYPES),
  DB_CONFIG: JSON.parse(process.env.SQL_DB_CONFIG),
  RO_TABLENAME: process.env.RO_TABLENAME,
  
  // DISTRICT_BOUNDARY : process.env.DISTRICT_BOUNDARY_NEW


  // isProd,
  // isProductionProject,
  // loggingService,
  // GCLOUD_PROJECT ,
  // TRANSACTION_LOGS_TABLE : process.env.TRANSACTION_LOGS_TABLE || 'transactionlogs',
  // CREDITS_TABLE : process.env.CREDITS_TABLE || 'credits'
}
