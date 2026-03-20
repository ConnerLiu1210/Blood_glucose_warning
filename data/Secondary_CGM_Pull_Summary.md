# Secondary_CGM_Cohort_Pull_Summary.md


## Overview
This workbook appears to be an secondary EHR file. It is not the main research summary database. Instead, it contains supporting raw hospital data tables that capture medication exposure, diet orders, carbohydrate intake, and tube feeding information. 

## Workbook structure
- Sheets observed:
  - Vasopressor
  - Steriod
  - Subcutaneous insulin doses
  - antibiotics IV Fluid(dextrose)
  - All_Diet_Orders
  - DIET_NPO_ORDER
  - DIET CARB CONTROLLED
  - DIET HEART HEALTHY
  - Flowsheets_carbs
  - DIETARY PLACE A TUBE FOOD

Interpretation：
This workbook functions as a supporting raw-detail file. Compared with REDCap:

---

## Sheet-by-sheet summary


## 1. Sheet: Vasopressor


### Likely meaning of columns
- `MRN`
  - medical record number
- `DAY_ENROLL`
  - study enrollment time
- `DAY_OFF`
  - study stop time 
- `MED_NAME`
  - medication name
- `taken_time`
  - administration timestamp
- `DOSE`
  - administered dose
- `DOSEUnit`
  - dose unit
- `form`
  - formulation
- `Route`
  - route of administration

Interpretation：
- severity-of-illness assessment
- studying whether pressor use affects CGM accuracy or glycemic variability


---

## 2. Sheet: Steriod

### Main columns
- `MRN`
- `DAY_ENROLL`
- `DAY_OFF`
- `MED_NAME`
- `TAKEN_TIME`
- `DOSE`
- `DoseUnit`
- `form`
- `ROUTE`

### What the sheet contains
This sheet contains steroid medication administration records.

Interpretation：
- Steroids are highly relevant because they can:
  - increase glucose levels
  - worsen hyperglycemia
  - alter insulin requirements

---

## 3. Sheet: Subcutaneous insulin doses

### Main columns
- `MRN`
- `DAY_ENROLL`
- `MED_NAME`
- `TAKEN_TIME`
- `sig`
- `Action`
- `DoseUnit`

### What the sheet contains
This sheet contains subcutaneous insulin(皮下胰岛素) administration records.

### Likely meaning of columns
- `MED_NAME`
  - insulin name
- `TAKEN_TIME`
  - administration time
- `sig`
  - dose instruction or recorded dose field
- `Action`
  - administration action, such as given
- `DoseUnit`
  - insulin unit field

Interpretation：
 This is one of the most important sheets for glucose analysis because it directly captures insulin treatment timing and intensity.


---

## 4. Sheet: antibiotics IV Fluid(dextrose)

### Main columns
- `MRN`
- `DAY_ENROLL`
- `MED_NAME`
- `DISPLAY_NAME`
- `taken_time`
- `DOSE`
- `DoseUnit`
- `route`
- `MAR_INFUSION_RATE`
- `MAR_INFUSION_RATE_UNIT`

### What the sheet contains
This sheet appears to mix:
- dextrose-containing IV fluids
- medications or antibiotics formulated in dextrose-containing infusions

Interpretation：
- Dextrose exposure can directly affect glucose readings and glycemic control. This makes the sheet valuable for:
  - identifying exogenous glucose exposure
  - explaining sudden hyperglycemia
  - adjusting interpretation of glucose trends

---

## 5. Sheet: All_Diet_Orders

### Main columns
- `MRN`
- `day_enroll`
- `ORDER_NAME`
- `ORDERING_DATE`
- `CATEGORY`

### What the sheet contains
This sheet contains all diet-related orders.

### Examples of order categories that may appear
- NPO
- carb-controlled diet
- tube feeding with tray
- modified texture diets


---

## 6. Sheet: DIET_NPO_ORDER(禁食名单)

### Main columns
- `MRN`
- `ADM_DATE_TIME`
- `ORDER_NAME`
- `ORDERING_DATE`

### What the sheet contains
This sheet specifically isolates NPO diet orders.

Interpretation：
- NPO status is important because it can:
  - reduce carbohydrate intake
  - change insulin needs
  - affect hypoglycemia/hyperglycemia risk

---

## 7. Sheet: DIET CARB CONTROLLED

### Main columns
- `MRN`
- `ADM_DATE_TIME`
- `ORDER_NAME`
- `ORDERING_DATE`

### What the sheet contains
This sheet captures carb-controlled diet orders.

Interpretation：
Directly relevant to glucose management because carbohydrate restriction or standardization can influence glycemic control and insulin dosing strategy.

---

## 8. Sheet: DIET HEART HEALTHY

### Main columns
- `MRN`
- `ADM_DATE_TIME`
- `ORDER_NAME`
- `ORDERING_DATE`

### What the sheet contains
This sheet captures heart-healthy diet orders.

Interpretation：
This is less directly glucose-specific than carb-controlled or NPO orders, but still helps characterize nutrition context and hospital diet assignment.

---

## 9. Sheet: Flowsheets_carbs

### Main columns
- `MRN`
- `DAY_ENROLL`
- `DAY_OFF`
- `item_name`
- `recorded_time`
- `meas_value`

### What the sheet contains
This sheet contains recorded carbohydrate- or intake-related flowsheet data.

### Examples of item types observed
- breakfast carb count
- lunch carb count
- dinner carb count
- calorie count

### Nature of the values
The `meas_value` field may contain:
- numeric carbohydrate values
- narrative intake descriptions
- meal completion notes

Interpretation：
This is a high-value sheet for nutrition–glucose linkage because it can provide more direct evidence of actual intake than diet orders alone.

---

## 10. Sheet: DIETARY PLACE A TUBE FOOD

### Main columns
- `MRN`
- `DAY_ENROLL`
- `MED_NAME`
- `display_name`
- `TAKEN_TIME`
- `DOSE`
- `Action`
- `DoseUnit`
- `route`
- `FREQ_NAME`

### What the sheet contains
This sheet appears to capture tube feeding or enteral nutrition administration records.



