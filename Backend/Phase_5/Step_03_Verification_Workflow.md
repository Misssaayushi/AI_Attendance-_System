# Step 03 - Verification Workflow

## Objective
Design the attendance verification workflow before writing API logic.

## Verification Pipeline
1. Authenticate admin/system request
2. Validate request payload
3. Fetch student record and verify active eligibility
4. Resolve attendance date context (server-side canonical date)
5. Apply duplicate prevention checks
6. Evaluate optional recognition confidence threshold
7. Accept or reject attendance mark with explicit reason

## Rule Strategy
- Verification is deterministic and service-layer controlled
- Rejections return consistent domain-specific errors
- Confidence rule toggles should be configurable

## Output of This Step
- Final rule sequence
- Decision table (accept/reject scenarios)
- Config points for threshold and timing behavior
