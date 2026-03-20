## Refined project formulation

### Prediction target
The model aims to predict whether glucose will reach a `High` state within the next 1 hour.

### Definition of `High`
In this project, `High` is defined as:
- a numeric glucose value greater than 400 mg/dL, or
- a glucose record explicitly labeled as `High`

This definition is based on the observed structure of the Dexcom Clarity log, where the maximum numeric glucose value is 400 mg/dL and values above that appear as `High`.

### Data selection strategy
To improve label reliability and input quality, the model will focus on the validated CGM/POC paired records from the `Full REDCap` dataset.

Preferred inclusion criteria:
- `Were ongoing CGM/POC value within 5 minutes?` = Yes
- `Was ongoing validation criteria met?` = Yes

This means the training data will be restricted to CGM/POC pairs that are both:
1. time-matched within 5 minutes
2. considered acceptable by the ongoing validation criteria

### Rationale
This strategy helps reduce noise from poorly aligned or low-confidence CGM values and ensures that the model is trained on more reliable glucose measurements.
