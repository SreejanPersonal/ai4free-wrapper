from datetime import datetime
from decimal import Decimal
import logging
from sqlalchemy.exc import SQLAlchemyError
from ..models.usage import Usage, ModelUsage, TotalAPIUsage, User
from ..extensions import db
from ..config import Config

log = logging.getLogger(__name__)

def record_request(user_id, api_key, model_id, prompt_tokens, completion_tokens, response_data):
    """
    Records a successful API request by updating:
      1. API Metrics table (Usage) for (api_key, model)
      2. Global Model Usage table (one row per model)
      3. Total API Usage table (singleton row)
      4. The corresponding user's usage record
    """
    try:
        now = datetime.utcnow()
        total_tokens = prompt_tokens + completion_tokens

        # Determine cost per million tokens for the model.
        cost_per_million = 0
        for model in Config.ALLOWED_MODELS:
            if model['id'] == model_id:
                cost_per_million = model.get('owner_cost_per_million_tokens', 0)
                break
        cost = (Decimal(total_tokens) / Decimal(1000000)) * Decimal(cost_per_million)

        # 1. Update API Metrics table (Usage)
        usage = Usage.query.filter_by(api_key=api_key, model=model_id).first()
        if not usage:
            usage = Usage(
                api_key=api_key, 
                model=model_id, 
                total_requests=0, 
                successful_requests=0, 
                failed_requests=0, 
                input_tokens=0, 
                output_tokens=0, 
                cost=0
            )
            db.session.add(usage)
        usage.total_requests = (usage.total_requests or 0) + 1
        usage.successful_requests = (usage.successful_requests or 0) + 1
        usage.input_tokens = (usage.input_tokens or 0) + prompt_tokens
        usage.output_tokens = (usage.output_tokens or 0) + completion_tokens
        usage.cost = (usage.cost or 0) + cost
        usage.last_updated = now

        # 2. Update Global Model Usage table (ModelUsage)
        model_usage = ModelUsage.query.filter_by(model=model_id).first()
        if not model_usage:
            model_usage = ModelUsage(
                model=model_id, 
                total_requests=0, 
                successful_requests=0, 
                failed_requests=0, 
                total_input_tokens=0, 
                total_output_tokens=0, 
                total_cost=0
            )
            db.session.add(model_usage)
        model_usage.total_requests = (model_usage.total_requests or 0) + 1
        model_usage.successful_requests = (model_usage.successful_requests or 0) + 1
        model_usage.total_input_tokens = (model_usage.total_input_tokens or 0) + prompt_tokens
        model_usage.total_output_tokens = (model_usage.total_output_tokens or 0) + completion_tokens
        model_usage.total_cost = (model_usage.total_cost or 0) + cost
        model_usage.last_updated = now

        # 3. Update Total API Usage table (TotalAPIUsage)
        total_usage = TotalAPIUsage.query.get(1)
        if not total_usage:
            total_usage = TotalAPIUsage(
                id=1, 
                total_requests=0, 
                successful_requests=0, 
                failed_requests=0, 
                total_input_tokens=0, 
                total_output_tokens=0, 
                total_cost=0
            )
            db.session.add(total_usage)
        total_usage.total_requests = (total_usage.total_requests or 0) + 1
        total_usage.successful_requests = (total_usage.successful_requests or 0) + 1
        total_usage.total_input_tokens = (total_usage.total_input_tokens or 0) + prompt_tokens
        total_usage.total_output_tokens = (total_usage.total_output_tokens or 0) + completion_tokens
        total_usage.total_cost = (total_usage.total_cost or 0) + cost

        # 4. Update the corresponding User record
        user = User.query.get(user_id)
        if user:
            user.total_requests = (user.total_requests or 0) + 1
            user.successful_requests = (user.successful_requests or 0) + 1
            user.total_input_tokens = (user.total_input_tokens or 0) + prompt_tokens
            user.total_output_tokens = (user.total_output_tokens or 0) + completion_tokens
            user.total_cost = (user.total_cost or 0) + cost
            user.last_request_time = now
            user.last_active = now

        # Update the APIKey record's model_usage column using a new dictionary instance
        from ..models.api_key import APIKey
        api_key_record = APIKey.query.filter_by(api_key=api_key, is_active=True).first()
        if api_key_record:
            current_usage = dict(api_key_record.model_usage) if api_key_record.model_usage else {}
            current_usage[model_id] = {
                "total_requests": usage.total_requests,
                "successful_requests": usage.successful_requests,
                "failed_requests": usage.failed_requests,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cost": str(usage.cost)
            }
            api_key_record.model_usage = current_usage

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        log.error(f"Database error recording usage: {e}")
    except Exception as e:
        db.session.rollback()
        log.exception(f"Unexpected error recording usage: {e}")

def record_failed_request(user_id, api_key, model_id):
    """
    Records a failed API request by updating:
      1. API Metrics table (Usage) for (api_key, model)
      2. Global Model Usage table (ModelUsage)
      3. Total API Usage table (TotalAPIUsage)
      4. The corresponding user's usage record
    """
    try:
        now = datetime.utcnow()

        # 1. Update API Metrics table (Usage) for failed request
        usage = Usage.query.filter_by(api_key=api_key, model=model_id).first()
        if not usage:
            usage = Usage(
                api_key=api_key, 
                model=model_id, 
                total_requests=0, 
                successful_requests=0, 
                failed_requests=0, 
                input_tokens=0, 
                output_tokens=0, 
                cost=0
            )
            db.session.add(usage)
        usage.total_requests = (usage.total_requests or 0) + 1
        usage.failed_requests = (usage.failed_requests or 0) + 1
        usage.last_updated = now

        # 2. Update Global Model Usage table (ModelUsage) for failed request
        model_usage = ModelUsage.query.filter_by(model=model_id).first()
        if not model_usage:
            model_usage = ModelUsage(
                model=model_id, 
                total_requests=0, 
                successful_requests=0, 
                failed_requests=0, 
                total_input_tokens=0, 
                total_output_tokens=0, 
                total_cost=0
            )
            db.session.add(model_usage)
        model_usage.total_requests = (model_usage.total_requests or 0) + 1
        model_usage.failed_requests = (model_usage.failed_requests or 0) + 1
        model_usage.last_updated = now

        # 3. Update Total API Usage table (TotalAPIUsage) for failed request
        total_usage = TotalAPIUsage.query.get(1)
        if not total_usage:
            total_usage = TotalAPIUsage(
                id=1, 
                total_requests=0, 
                successful_requests=0, 
                failed_requests=0, 
                total_input_tokens=0, 
                total_output_tokens=0, 
                total_cost=0
            )
            db.session.add(total_usage)
        total_usage.total_requests = (total_usage.total_requests or 0) + 1
        total_usage.failed_requests = (total_usage.failed_requests or 0) + 1

        # 4. Update the corresponding User record for failed request
        user = User.query.get(user_id)
        if user:
            user.total_requests = (user.total_requests or 0) + 1
            user.failed_requests = (user.failed_requests or 0) + 1
            user.last_request_time = now
            user.last_active = now

        # Update the APIKey record's model_usage column using a new dictionary instance
        from ..models.api_key import APIKey
        api_key_record = APIKey.query.filter_by(api_key=api_key, is_active=True).first()
        if api_key_record:
            current_usage = dict(api_key_record.model_usage) if api_key_record.model_usage else {}
            current_usage[model_id] = {
                "total_requests": usage.total_requests,
                "successful_requests": usage.successful_requests,
                "failed_requests": usage.failed_requests,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cost": str(usage.cost)
            }
            api_key_record.model_usage = current_usage

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        log.error(f"Database error recording failed request: {e}")
    except Exception as e:
        db.session.rollback()
        log.exception(f"Unexpected error recording failed request: {e}")