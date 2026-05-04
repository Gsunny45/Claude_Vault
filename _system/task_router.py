"""
Task Router: Production-grade task classification and role mapping.

STAGING (2026-04-20): Temporary home is Claude_Vault/_system/.
Permanent target: Local-Network-Hub/routing/task_router.py — migrate when TSK-0009
(scaffold Local-Network-Hub) is complete. Do NOT import from Obsidian plugins.

Core pattern extracted from COG Foundation architecture.
Maps complex task descriptions to optimal AI role assignments using pattern matching
and circuit breaker fault tolerance.

Roles available:
  - coder: Code generation, debugging, refactoring
  - searcher: Research, information retrieval, fact-finding
  - planner: Strategic thinking, workflow design, decomposition
  - leader: Complex multi-step coordination, synthesis
  - workhorse: Bulk operations, repetitive tasks, parallelizable work

Usage:
    cb = CircuitBreaker(failure_threshold=3, timeout=60)
    router = SmartRouter(cb)
    role = router.classify_task("Write a Python function that validates email addresses")
    # Returns: "coder"
"""

from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time


class TaskRole(Enum):
    """Available AI role assignments."""
    CODER = "coder"
    SEARCHER = "searcher"
    PLANNER = "planner"
    LEADER = "leader"
    WORKHORSE = "workhorse"


@dataclass
class CircuitBreaker:
    """
    Fault tolerance for task routing.
    Prevents cascading failures when providers are degraded.
    """
    failure_threshold: int = 3
    timeout: int = 60
    recovery_timeout: int = 300

    def __post_init__(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def record_failure(self):
        """Record a failure event."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"

    def record_success(self):
        """Record a successful call."""
        self.failure_count = max(0, self.failure_count - 1)
        if self.failure_count == 0:
            self.state = "closed"

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        Raises exception if circuit is open.
        """
        if self.state == "open":
            elapsed = time.time() - (self.last_failure_time or 0)
            if elapsed > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise Exception(f"Circuit breaker is open. Retry in {self.recovery_timeout - elapsed:.0f}s")

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class SmartRouter:
    """
    Task classification engine mapping natural language descriptions to AI roles.
    
    Implements pattern-based routing with configurable role mappings.
    Production-grade with fault tolerance via circuit breaker.
    """

    def __init__(self, circuit_breaker: Optional[CircuitBreaker] = None):
        """
        Initialize router with optional circuit breaker.
        
        Args:
            circuit_breaker: Fault tolerance control (optional)
        """
        self.cb = circuit_breaker or CircuitBreaker()

        # Pattern keyword mappings for role classification
        self.TASK_ROUTING: Dict[str, TaskRole] = {
            "code": TaskRole.CODER,
            "function": TaskRole.CODER,
            "script": TaskRole.CODER,
            "refactor": TaskRole.CODER,
            "debug": TaskRole.CODER,
            "algorithm": TaskRole.CODER,
            "implement": TaskRole.CODER,
            "search": TaskRole.SEARCHER,
            "research": TaskRole.SEARCHER,
            "find": TaskRole.SEARCHER,
            "lookup": TaskRole.SEARCHER,
            "investigate": TaskRole.SEARCHER,
            "explore": TaskRole.SEARCHER,
            "plan": TaskRole.PLANNER,
            "design": TaskRole.PLANNER,
            "architect": TaskRole.PLANNER,
            "strategy": TaskRole.PLANNER,
            "workflow": TaskRole.PLANNER,
            "decompose": TaskRole.PLANNER,
            "complex": TaskRole.LEADER,
            "coordinate": TaskRole.LEADER,
            "synthesize": TaskRole.LEADER,
            "integrate": TaskRole.LEADER,
            "orchestrate": TaskRole.LEADER,
            "bulk": TaskRole.WORKHORSE,
            "batch": TaskRole.WORKHORSE,
            "process": TaskRole.WORKHORSE,
            "iterate": TaskRole.WORKHORSE,
            "parallel": TaskRole.WORKHORSE,
        }

    def classify_task(self, task_description: str) -> TaskRole:
        """
        Classify a task into an AI role based on keywords and patterns.
        
        Args:
            task_description: Natural language task description
            
        Returns:
            TaskRole enum indicating the best-fit AI role
            
        Raises:
            Exception: If circuit breaker is open (service degraded)
        """
        def _classify():
            # Normalize input
            normalized = task_description.lower().strip()

            # Keyword-based routing (pattern matching)
            for keyword, role in self.TASK_ROUTING.items():
                if keyword in normalized:
                    return role

            # Length heuristic: very long descriptions → leader
            if len(normalized) > 200:
                return TaskRole.LEADER

            # Default fallback
            return TaskRole.PLANNER

        # Wrap with circuit breaker protection
        return self.cb.call(_classify)

    def smart_call(
        self,
        task: str,
        provider_map: Dict[TaskRole, Callable],
        fallback: Optional[Callable] = None,
    ):
        """
        Route task to appropriate provider based on classification.
        
        Args:
            task: Task description
            provider_map: Mapping of TaskRole → callable provider
            fallback: Fallback provider if role not in map
            
        Returns:
            Result from routed provider
        """
        role = self.classify_task(task)
        provider = provider_map.get(role, fallback)

        if not provider:
            raise ValueError(f"No provider for role {role} and no fallback")

        return provider(task)


# Example integration points (uncomment to use with message bus)
"""
def post_to_bus(self, msg: Message) -> bool:
    '''Post classified task to message bus for async processing.'''
    role = self.classify_task(msg.payload.get("task", ""))
    msg.metadata["assigned_role"] = role.value
    return self.bus.post(msg)


def claim_from_bus(self, consumer_id: str) -> Optional[Message]:
    '''Claim task from bus matching this router's role preferences.'''
    msg = self.bus.claim(consumer_id)
    if msg:
        assigned_role = msg.metadata.get("assigned_role")
        if assigned_role:
            msg.metadata["claimed_role"] = assigned_role
    return msg


def complete_bus_task(self, msg: Message, result: Dict) -> bool:
    '''Mark bus task complete with role information.'''
    result["processed_role"] = msg.metadata.get("assigned_role", "unknown")
    return self.bus.complete(msg, result)
"""
