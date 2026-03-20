# Full_REDCap_Data_Summary.md


## Overview
This file is the primary research database for the Dexcom intervention study. It contains baseline information together with repeated daily research forms. In practice, it functions as the main analytic dataset. 

## General data summary

- Data organization:
  - One main record per subject 
  - Multiple repeated instruments for daily follow-up
- Major record groups observed:
  - Baseline/Main record
  - Daily Clinical Condition and Use
  - Daily Medications
  - Daily Insulin Dosing
  - Daily Hospital Labs
  - Daily Protocol Fidelity and Safety
  - Daily Ongoing CGM/POC Pairs

## Core identifying columns
Common top-level columns include:
- Unique Study ID(subject identifier)
- Repeat Instrument`(which repeated form the row belongs to)
- Repeat Instance(the repeat sequence number)
- Data Access Group(REDCap access grouping)


## Main content areas

### 1. Baseline and demographic information(病人基本信息)
Examples of variables:
- Dexcom
- Age
- Race
- Latino
- Sex
- Height (cm)
- Weight (kg)
- BMI

What this section captures:
- basic demographics
- body size measurements

### 2. Diabetes history and outpatient glucose treatment(糖尿病病史)
Examples of variables:
- History of DM?
- DM type
- Admission HbA1C
- Admission glucose
- Glucose-lowering medication variables:
Biguanides, Sulfonylureas/Meglitinides, DPP-4 Inhibitors, SGLT-2 inhibitors, TZDs, GLP-1 receptor agonists, Other (non-insulin)
- insulin prior to admission variables
- Estimated total daily dose (TDD)

What this section captures:
- diabetes status and type
- chronic antihyperglycemic therapy before admission
- pre-admission insulin exposure

### 3. Past medical history and comorbidities(其他病史)
Examples of variables:
- History of tobacco use
- History of COPD?
- History of asthma?
- History of Hypertension?
- History of heart failure?
- History of CAD?

What this section captures:
- major chronic medical conditions
- potential factors for inpatient glucose control and CGM performance

### 4. Admission and ICU context(入院信息)
Examples of variables:
- Admit Diagnosis
- Admitting Service
- MICU location
- MICU floor
- DKA/HHNK on admission?
- clinical condition on admission checkboxes

What this section captures:
- admission diagnosis and service
- ICU setting
- severity of illness context

### 5. Kidney function and dialysis(肾功能和透析情况)
Examples of variables:
- Admission eGFR
- Admission creatinine
- doubling of creatinine variables
- dialysis status variables
- dialysis type variables

What this section captures:
- renal function at enrollment
- renal injury severity
- dialysis exposure, which may influence CGM accuracy and glucose management

### 6. Clinical status at CGM placement(CGM临床情况)
Examples of variables:
- intubation status at CGM placement
- oxygen support
- heart disease status
- stroke/MI/cardiac arrest-related variables

What this section captures:
- physiologic condition at the time of sensor insertion

### 7. Sensor placement and removal tracking(传感器情况)
Examples of variables:
- Date/time of sensor  insertion?
- Sensor duration (days)
- Sensor number of values recorded in the EHR?
- Staff placing sensor?
- Time/date that sensor was stopped
- Early sensor removal prior to 10 days
- similar fields through additional sensors

What this section captures:
- when each Dexcom sensor was placed and removed
- duration of use
- whether removal was early


## Repeated daily instruments(每日重复记录表单)

### A. Daily Clinical Condition and Use(每日临床情况)
Examples of variables:
- Date
- dialysis status/type
- ECMO status
- mechanical ventilation
- extubation
- supplemental oxygen
- high-flow oxygen
- acetaminophen dose
- thromboembolic event
- enteral nutrition
- TPN
- mortality
- sensor site bruising, erythema, infection
- loss of signal events
- remote monitoring device/method

What this section captures:
- day-by-day illness severity and support measures
- nutrition support exposure
- sensor site safety events

### B. Daily Medications(每日用药记录)
Examples of variables:
- Date
- pressor support status
- number of pressors
- specific vasopressors used
- highest vasopressor dose in that calendar day
- steroid exposure
- steroid type
- daily steroid dose
- acetaminophen exposure and total daily dose

What this section captures:
- vasoactive medication exposure
- steroid exposure
- medication-related factors that may alter glucose patterns or CGM performance

### C. Daily Insulin Dosing(每日胰岛素剂量记录)
Examples of variables:
- Date
- IV insulin status
- total daily IV insulin units
- subcutaneous insulin status
- total bolus insulin units
- basal insulin units
- NPH or mixed insulin exposure
- daily NPH units

What this section captures:
- daily inpatient insulin 
- route and intensity of insulin therapy

### D. Daily Hospital Labs(实验室记录)
Examples of variables:
- Date
- Creatinine (mg/dl)
- eGFR
- Procalcitonin
- CRP
- Troponin
- IL6
- ALT
- AST
- TBR
- WBC
- Absolute lymphocyte count
- Ferritin
- D-dimer
- pH
- BHB
- Bicarbonate
- INR
- PTT
- Complete?

What this section captures:
- renal, inflammatory, hepatic, cardiac, and coagulation markers
- metabolic acidosis/ketosis-related measurements
- daily physiologic context for glucose instability

### E. Daily Protocol Fidelity and Safety(每日方案执行情况与安全性)
Examples of variables:
- initial validation fields
- first and second CGM/POC paired values
- timing comparison within 5 minutes
- whether validation criteria were met
- multiple clinical trigger variables in prior 24 hours
- Clarity-based glycemic metrics
- daily counts of POC and CGM values
- notes from daily rounds

What this section captures:
- whether the study protocol was followed correctly
- CGM safety checks
- clinical events that require renewed caution or revalidation
- summarized daily glycemic performance from Clarity

### F. Daily Ongoing CGM/POC Pairs(CGM/POC配对记录)
Examples of variables:
- Date
- ongoing CGM value and timestamp
- ongoing POC value and timestamp
- POC source
- whether values were within 5 minutes
- whether ongoing validation criteria were met
- nearby oxygen saturation, PaO2, MAP, and blood pressure fields

What this section captures:
- repeated CGM-to-POC comparison pairs
- ongoing accuracy monitoring
- physiologic conditions near each comparison time point

# Data Analysis Summary
## 1. Overall file structure
- Total rows: 6686
- Total columns: 284
- Unique subjects: 101

## 2. Record type distribution
- Baseline/Main record: 101
- Daily Clinical Condition and Use: 529
- Daily Medications: 529
- Daily Insulin Dosing: 529
- Daily Hospital Labs: 529
- Daily Protocol Fidelity and Safety: 529
- Daily Ongoing CGM/POC Pairs: 3940

Interpretation:
- Each subject has about 5 days of daily follow-up on average.

## 3. Baseline characteristics
### Demographics
- Mean age: 54.6 years
- Age range: 22–83 years
- Mean BMI: 31.35
- Sex distribution is nearly balanced:
  - Male: 53
  - Female: 47

### Race
- White: 83
- Black: 15
- Other: 2

### Dexcom use
- Yes: 96
- No: 3

Interpretation:
- This is primarily a middle-aged cohort with relatively high BMI.
- Most subjects were actual Dexcom users.

## 4. Diabetes-related characteristics
### History of diabetes
- Yes: 86
- No: 14

### Diabetes type
- Type 2 diabetes: 59
- Type 1 diabetes: 26

### Glycemic status at admission
- Mean admission HbA1c: 8.08
- Mean admission glucose: 297.2 mg/dL
- Admission glucose range: 27–1059 mg/dL

Interpretation:
- The cohort is predominantly composed of patients with diabetes, especially type 2 diabetes.
- Admission glucose levels were generally high and highly variable.

## 5. Comorbidity burden
- Hypertension(高血压）: 75
- CAD: 23
- COPD: 22
- Asthma(哮喘): 16
- Heart failure: about 21

Interpretation:
- The cohort carries a substantial comorbidity burden.
- These conditions may affect both inpatient glucose control and CGM performance.

## 6. Daily clinical status
- Dialysis(透析): 130/529
- Mechanical ventilation(机器通气): 297/529
- Supplemental oxygen(供氧): 139/529
- Enteral nutrition(肠内营养): 319/529
- TPN: 5/529
- Mortality: 5/529

Interpretation:
- This is a clinically severe inpatient cohort.
- Mechanical ventilation, dialysis, and enteral nutrition were relatively common.
- TPN was uncommon.

## 7. Daily medication exposure
### Vasopressors(升压药物)
- Daily pressor support: 153/529
- Most common vasopressor: norepinephrine(去甲肾上腺素)

### Steroids(激素)
- Steroid exposure: 253/529

### Acetaminophen(对乙酰氨基酚)
- Exposure: 165/529

Interpretation:
- Vasopressor and steroid exposure were common.
- These are important factors when evaluating glucose patterns and CGM performance.

## 8. Daily insulin treatment
- IV insulin(静脉): 337/529
- Subcutaneous insulin(皮下): 324/529
- NPH/mixed insulin(混合): 29/529

Interpretation:
- Both IV and subcutaneous insulin were commonly used.

## 9. Daily laboratory data
The most consistently available lab variables include:
- Creatinine(肌酐)
- eGFR
- WBC(白细胞数目)
- Bicarbonate(碳酸氢根)

Interpretation:
- Renal function, inflammation/infection-related markers, and acid-base status are relatively well represented.
- Other markers such as CRP, D-dimer, and BHB are less consistently available.

## 10. CGM and POC validation
### Ongoing CGM/POC pairs
- Total records: 3940
- Paired within 5 minutes: 2043
- Ongoing validation criteria met: 2386

### Conditions near paired measurements
- Low oxygen events were present
- MAP(平均动脉压) < 65 also occurred in a meaningful number of paired records(灌注差,血糖数据偏差大，CGM和POC一致性受影响）

Interpretation:
- The dataset contains a large number of CGM/POC paired records.
- Some pairs occurred during low-oxygen or low-perfusion states

## Inferred Matching Rule for Ongoing CGM/POC Validation

### Time matching rule
Based on the field:

- `Were ongoing CGM/POC value within 5 minutes?`

the table clearly uses a time-based pairing rule.  
A CGM value and a POC value are considered time-matched when their timestamps are within 5 minutes of each other.

### Glucose difference rule
The table does not explicitly provide the numeric threshold used to determine whether a paired CGM/POC comparison passed validation. It only records the final result in the field:

- `Was ongoing validation criteria met?`

However, based on the observed CGM and POC values in the paired records, the validation rule appears to be approximately:

- the CGM value is within about 20% of the POC value

This can be expressed as:

|CGM - POC|/POC <= 20%

### Why this rule was inferred
This inference is based on the following observations:

- the dataset records both time matching (`within 5 minutes`) and whether ongoing validation criteria were met
- when paired CGM and POC values are compared, a relative difference threshold of about 20% matches the observed Yes/No validation results well
- using a 20% threshold gives an agreement rate of about 95.7% with the recorded validation outcomes


