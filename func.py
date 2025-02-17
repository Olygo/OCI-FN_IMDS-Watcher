###############################################################
#   This functions force IMDSv2 on compute instance           # 
#   func.py                                      #
#   Florian Bonneville                                        #
#   2025-02-17                                                #
#   1.0.0                                                     #
###############################################################

import io
import os
import json
import oci
import time
import random
import logging
from fdk import response

# Set oci logging at Warning level
logging.getLogger('oci').setLevel(logging.WARNING)
# Set oci.circuit_breaker logging at Warning level
logging.getLogger("oci.circuit_breaker").setLevel(logging.WARNING)

def configure_logger(log_level=logging.INFO, include_level=False, include_module=False, include_message=True):

    # set up logger
    logging.basicConfig(level=log_level)
    logger=logging.getLogger(__name__)

    # define a custom format for the logger
    format_string=''
    if include_level:
        format_string += '%(levelname)s - '
    if include_module:
        format_string += '%(module)s - '
    if include_message:
        format_string += '%(message)s'

    formatter=logging.Formatter(format_string)

    # apply the custom format to the logger
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)

    return logger

# set loggers with desired log level and module name
logger_info=configure_logger(log_level=logging.INFO, include_level=True, include_module=False)
log_info=logger_info.info

logger_warning=configure_logger(log_level=logging.WARNING, include_level=True, include_module=False)
log_warning=logger_warning.warning

logger_error=configure_logger(log_level=logging.ERROR, include_level=True, include_module=False)
log_error=logger_error.error

logger_critical=configure_logger(log_level=logging.WARNING, include_level=True, include_module=False)
log_critical=logger_critical.critical


def get_instance_details(log_header, compute_client, instance_ocid):

    try:
        instance_details=compute_client.get_instance(instance_id=instance_ocid).data
        return instance_details
    
    except Exception as e:
        log_critical(f"{log_header}: An error occured in: {get_instance_details.__name__} :{e}")
        raise

def update_imds(log_header, compute_client, instance):

    log_info(f"{log_header}: {instance.display_name}: Updating...")

    try:
        update_instance_response = compute_client.update_instance(
            instance_id=instance.id,
            update_instance_details=oci.core.models.UpdateInstanceDetails(
                instance_options=oci.core.models.InstanceOptions(
                    are_legacy_imds_endpoints_disabled=True)
                    ))
        time.sleep(2)
        updated_instance=get_instance_details(log_header, compute_client, instance.id)

        log_info(f"{log_header}: {updated_instance.display_name} IMDSv2: {updated_instance.instance_options.are_legacy_imds_endpoints_disabled}")
        
        return #update_instance_response.data

    except Exception as e:
        log_critical(f"{log_header}: An error occured in: {update_imds.__name__}: {e}")
        raise

def handler(ctx, data: io.BytesIO=None):

    # initialize oci clients
    signer=oci.auth.signers.get_resource_principals_signer()
    compute_client=oci.core.ComputeClient(config={}, signer=signer)

    try:

        # parse response body
        body=json.loads(data.getvalue())
        #log_info(f"body: {body}")

        eventType=body.get("eventType")
        #cloudEventsVersion=body.get("cloudEventsVersion")
        #eventTypeVersion=body.get("eventTypeVersion")
        #eventTime=body.get("eventTime")
        #source=body.get("source")

        #body_data=body["data"]
        #log_info(f"body: {body_data}")
        resourceId=body["data"].get("resourceId")
        #compartmentId=body["data"].get("compartmentId")
        compartmentName=body["data"].get("compartmentName")
        #resourceName=body["data"].get("resourceName")
        #availabilityDomain=body["data"].get("availabilityDomain")
        #freeformTags=body["data"].get("freeformTags")
        #definedTags=body["data"].get("definedTags")
        #volumeId=body["data"]["additionalDetails"].get("volumeId")
        #imageId=body["data"]["additionalDetails"].get("imageId")
        #shape=body["data"]["additionalDetails"].get("shape")

        # set random seed for log id
        # use current timestamp as seed
        #random.seed(time.time())
        # retrieve 16 random bytes from os as seed
        random.seed(os.urandom(16))

        log_header=ctx.Config().get("log_header", "")
        log_header=f"log_header_{random.randint(0, 999)}" if log_header else f"FN_IMDS_UPDATE_{random.randint(0, 999)}"

        instance=get_instance_details(log_header,compute_client, resourceId)
        log_info(f"{log_header}: {compartmentName}/{instance.display_name}: {eventType}")
        update_imds(log_header, compute_client, instance)

    except Exception as e:
        log_critical(f"{log_header}: Handler failed:{e}")
        raise

    return response.Response(
        ctx,
        response_data=json.dumps(body),
        headers={"Content-Type": "application/json"}
    )