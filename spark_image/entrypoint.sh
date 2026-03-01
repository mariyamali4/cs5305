#!/bin/bash

# Ensure directories have proper permissions for spark user
mkdir -p /opt/spark/spark-events /opt/spark/worker-logs /opt/spark/worker-data /opt/spark/warehouse /opt/spark/delta
chown -R spark:spark /opt/spark/spark-events /opt/spark/worker-logs /opt/spark/worker-data /opt/spark/warehouse /opt/spark/delta 2>/dev/null || true
chmod -R u+rwX,g+rwX,o+rX /opt/spark/spark-events /opt/spark/worker-logs /opt/spark/worker-data /opt/spark/warehouse /opt/spark/delta 2>/dev/null || true

# Set environment variables for spark user
export JAVA_HOME=/opt/java/openjdk
export SPARK_HOME=/opt/spark
export HOME=/home/spark
export PATH=$PATH:$SPARK_HOME/bin

if [ "$SPARK_MODE" = "MASTER" ]; then
    # Start Spark Master
    su - spark -c "export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export PATH=$PATH; /opt/spark/sbin/start-master.sh --properties-file /opt/spark/conf/spark-master.conf &"
    # Start Spark Connect Server  
    su - spark -c "export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export PATH=$PATH; /opt/spark/sbin/start-connect-server.sh --properties-file /opt/spark/conf/spark-connect-server.conf &"
    # Start Spark History Server
    su - spark -c "export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export PATH=$PATH; /opt/spark/sbin/start-history-server.sh --properties-file /opt/spark/conf/spark-history-server.conf &"
    # Keep container running
    tail -f /dev/null
elif [ "$SPARK_MODE" = "WORKER" ]; then
    # Start Spark Worker
    exec su - spark -c "export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export PATH=$PATH; /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker --properties-file /opt/spark/conf/spark-worker.conf spark://spark-master:7077"
elif [ "$SPARK_MODE" = "JUPYTER" ]; then
    # Start Jupyter Server
    exec su - spark -c "
            export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export HOME=$HOME; export PATH=$PATH; \
            jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
                --IdentityProvider.token='' --ServerApp.disable_check_xsrf=True \
                --ServerApp.allow_origin='*' --notebook-dir=/home/spark"
else
    echo "Invalid SPARK_MODE: $SPARK_MODE. Must be MASTER, WORKER, or JUPYTER."
    exit 1
fi