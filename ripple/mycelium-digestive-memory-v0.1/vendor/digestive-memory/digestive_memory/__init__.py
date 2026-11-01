"""Digestive Memory: source-linked, scoped, temporal external memory."""
from .contracts import Candidate, Event, Policy, Receipt, Recall, Scope
from .engine import Memory

__all__ = ['Memory', 'Candidate', 'Event', 'Scope', 'Policy', 'Receipt', 'Recall']
__version__ = '0.1.0'
