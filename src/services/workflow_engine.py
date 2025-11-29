"""
Workflow automation engine for business process automation.
"""
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from src.database.base import SessionLocal

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Types of workflow triggers."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    CONDITION = "condition"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    id: str
    name: str
    action_type: str
    action_config: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    on_success: Optional[str] = None  # Next step ID
    on_failure: Optional[str] = None  # Next step ID
    timeout: Optional[int] = None  # Timeout in seconds


@dataclass
class WorkflowDefinition:
    """Defines a complete workflow."""
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class WorkflowEngine:
    """Core workflow automation engine."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.running_workflows: Dict[str, Dict[str, Any]] = {}
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register default action handlers."""
        self.register_action("send_email", self._action_send_email)
        self.register_action("create_record", self._action_create_record)
        self.register_action("update_record", self._action_update_record)
        self.register_action("send_notification", self._action_send_notification)
        self.register_action("execute_ai_task", self._action_execute_ai_task)
        self.register_action("wait", self._action_wait)
        self.register_action("condition", self._action_condition)
    
    def register_action(self, action_type: str, handler: Callable):
        """Register a custom action handler."""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered action handler: {action_type}")
    
    def create_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """Create a new workflow definition."""
        try:
            self.workflows[workflow_def.id] = workflow_def
            logger.info(f"Created workflow: {workflow_def.name} ({workflow_def.id})")
            return True
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow definition by ID."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[WorkflowDefinition]:
        """List all workflow definitions."""
        return list(self.workflows.values())
    
    def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": f"Workflow {workflow_id} not found"}
        
        if not workflow.enabled:
            return {"success": False, "error": f"Workflow {workflow_id} is disabled"}
        
        execution_id = f"{workflow_id}_{datetime.utcnow().timestamp()}"
        context = context or {}
        context["execution_id"] = execution_id
        context["workflow_id"] = workflow_id
        
        self.running_workflows[execution_id] = {
            "workflow_id": workflow_id,
            "status": WorkflowStatus.RUNNING,
            "started_at": datetime.utcnow(),
            "context": context,
            "current_step": None,
            "completed_steps": [],
            "errors": []
        }
        
        try:
            result = self._execute_steps(workflow, context)
            self.running_workflows[execution_id]["status"] = WorkflowStatus.COMPLETED
            self.running_workflows[execution_id]["completed_at"] = datetime.utcnow()
            return result
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            self.running_workflows[execution_id]["status"] = WorkflowStatus.FAILED
            self.running_workflows[execution_id]["errors"].append(str(e))
            return {"success": False, "error": str(e), "execution_id": execution_id}
    
    def _execute_steps(self, workflow: WorkflowDefinition, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps."""
        if not workflow.steps:
            return {"success": True, "message": "No steps to execute"}
        
        current_step_id = workflow.steps[0].id if workflow.steps else None
        
        while current_step_id:
            step = next((s for s in workflow.steps if s.id == current_step_id), None)
            if not step:
                break
            
            self.running_workflows[context["execution_id"]]["current_step"] = step.id
            
            # Check conditions
            if not self._evaluate_conditions(step.conditions, context):
                logger.info(f"Step {step.id} conditions not met, skipping")
                current_step_id = step.on_failure or None
                continue
            
            # Execute action
            try:
                result = self._execute_action(step, context)
                context.update(result.get("context_updates", {}))
                self.running_workflows[context["execution_id"]]["completed_steps"].append(step.id)
                
                if result.get("success"):
                    current_step_id = step.on_success or None
                else:
                    current_step_id = step.on_failure or None
                    
            except Exception as e:
                logger.error(f"Error executing step {step.id}: {e}")
                self.running_workflows[context["execution_id"]]["errors"].append(f"Step {step.id}: {str(e)}")
                current_step_id = step.on_failure or None
        
        return {"success": True, "context": context, "execution_id": context["execution_id"]}
    
    def _execute_action(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow action."""
        handler = self.action_handlers.get(step.action_type)
        if not handler:
            raise ValueError(f"Unknown action type: {step.action_type}")
        
        logger.info(f"Executing action: {step.action_type} in step {step.id}")
        return handler(step.action_config, context)
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """Evaluate workflow conditions."""
        if not conditions:
            return True
        
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            context_value = context.get(field)
            
            if operator == "equals" and context_value != value:
                return False
            elif operator == "not_equals" and context_value == value:
                return False
            elif operator == "greater_than" and not (context_value > value):
                return False
            elif operator == "less_than" and not (context_value < value):
                return False
            elif operator == "contains" and value not in str(context_value):
                return False
        
        return True
    
    # Default Action Handlers
    def _action_send_email(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send email action."""
        # This will be implemented with email service
        logger.info(f"Sending email: {config.get('to')}")
        return {"success": True, "message": "Email sent"}
    
    def _action_create_record(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create database record action."""
        model_type = config.get("model_type")
        data = config.get("data", {})
        
        # This will be implemented with service layer
        logger.info(f"Creating {model_type} record")
        return {"success": True, "context_updates": {f"{model_type}_id": 1}}
    
    def _action_update_record(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update database record action."""
        model_type = config.get("model_type")
        record_id = config.get("record_id")
        data = config.get("data", {})
        
        logger.info(f"Updating {model_type} record {record_id}")
        return {"success": True}
    
    def _action_send_notification(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification action."""
        message = config.get("message", "")
        logger.info(f"Sending notification: {message}")
        return {"success": True}
    
    def _action_execute_ai_task(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI-powered task."""
        task = config.get("task", "")
        prompt = config.get("prompt", "")
        
        # This will use AIService
        logger.info(f"Executing AI task: {task}")
        return {"success": True, "context_updates": {"ai_result": "Task completed"}}
    
    def _action_wait(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Wait action (delay)."""
        import time
        seconds = config.get("seconds", 0)
        time.sleep(seconds)
        return {"success": True}
    
    def _action_condition(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Conditional action."""
        condition = config.get("condition", {})
        result = self._evaluate_conditions([condition], context)
        return {"success": result}
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status."""
        return self.running_workflows.get(execution_id)
    
    def close(self):
        """Close database session."""
        self.db.close()

