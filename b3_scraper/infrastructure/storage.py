"""
b3_scraper.infrastructure.storage
Persistência de registros, enviando arquivos Parquet ao S3.
"""
import logging
import json
from datetime import datetime
from typing import List
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

import io
import pandas as pd

from b3_scraper.domain.models import TradeRecord

logger = logging.getLogger(__name__)

class Storage:
    """
    Faz upload de listas de TradeRecord para um bucket S3 como arquivo Parquet.
    """
    def __init__(self, bucket: str, region: str, prefix: str):
        """
        :param bucket: nome do bucket S3
        :param region: região AWS
        :param prefix: prefixo/pasta dentro do bucket
        """
        self.bucket = bucket
        self.prefix = prefix.rstrip('/')
        # Inicializa cliente S3
        # self.s3 = boto3.client('s3', region_name=region)
        # Exchange environment role ARN if provided
        role_arn = os.getenv('AWS_ROLE_ARN')
        if role_arn:
            sts = boto3.client('sts', region_name=region)
            assumed = sts.assume_role(RoleArn=role_arn, RoleSessionName='b3-scraper-session')
            creds = assumed['Credentials']
            self.s3 = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=creds['AccessKeyId'],
                aws_secret_access_key=creds['SecretAccessKey'],
                aws_session_token=creds['SessionToken']
            )
            logger.debug("Assumed role %s and created S3 client with temporary credentials", role_arn)
        else:
            self.s3 = boto3.client('s3', region_name=region)

    def save_records(self, records: List[TradeRecord]) -> None:
        """
        Persiste os registros no bucket S3 em arquivos Parquet particionados por data.
        :param records: lista de TradeRecord
        """
        df = pd.DataFrame([record.__dict__ for record in records])
        df['record_date'] = pd.to_datetime(df['record_date']).dt.strftime('%Y-%m-%d')
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        # Particionamento alterado de date=YYYY-MM-DD para ano=YYYY/mes=MM/dia=DD para compatibilizar com Glue/Athena.
        for record_date, group in df.groupby('record_date'):
            buf = io.BytesIO()
            group.to_parquet(buf, index=False)
            buf.seek(0)
            key = (f"{self.prefix}/ano={record_date[0:4]}/mes={record_date[5:7]}/dia={record_date[8:10]}/"
                   f"trade_records_{timestamp}.parquet")
            try:
                self.s3.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=buf.getvalue(),
                    ContentType='application/octet-stream'
                )
                logger.info("Successfully uploaded %d records for date %s as Parquet to s3://%s/%s", len(group), record_date, self.bucket, key)
            except (BotoCoreError, ClientError) as e:
                logger.error("Failed to upload Parquet records for date %s to S3: %s", record_date, e)
                raise