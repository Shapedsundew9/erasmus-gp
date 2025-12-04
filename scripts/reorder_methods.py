"""Reorder methods script.
# **Specification: Python Source Code Method & Function Reorganizer**

## **1. Objective**

Create a command-line utility in Python 3.12+ that recursively traverses a directory tree,
identifies Python source files (.py), and reorganizes the order of function and class method
definitions according to a specific visibility and naming hierarchy.

## **2. Core Sorting Logic**

The script must reorder definitions based on the following precedence (from top to bottom):

### **A. Class Scope (Methods)**

1. **Constructor:** __init__ is always first.
2. **Dunder Methods:** Methods starting and ending with __ (excluding __init__),
     sorted alphabetically (e.g., __repr__, __str__).
3. **Private Methods:** Methods starting with a single _ (e.g., _internal_calc), sorted
    alphabetically.
   * *Note:* Any method starting with _ that does not end with __ is considered private.
4. **Public Methods:** All other methods (e.g., calculate_total), sorted alphabetically.

### **B. Module Scope (Functions)**

1. **Standalone Functions:** All top-level functions sorted alphabetically.
   * *Constraint:* Do not mix functions with classes. Functions should be sorted amongst
     themselves, but their relative position to classes (e.g., if functions are typically at
     the bottom of the file) should ideally be maintained or they should be grouped together.
     *Decision for MVP:* Sort all top-level functions relative to each other, but keep classes
     and functions in their original "blocks" if possible, or simple alphabetical sort of all
     functions, leaving classes where they are.

## **3. Preservation Requirements (Critical)**

The script must strictly preserve:

1. **Decorators:** @decorator lines must move with the function they decorate.
2. **Leading Comments:** # comments immediately preceding a function definition
    (or its decorators) must move with that function.
3. **Docstrings:** Function/Method docstrings must remain inside the function.
4. **Type Hints:** Python 3.12 type syntax and from __future__ import annotations must be respected.
5. **Indentation:** Relative indentation must be preserved (critical for nested scopes).
6. **Asynchronous Functions:** async def must be treated identically to def.
"""

# TODO: Implement the reorder_methods.py script according to the above specification.
