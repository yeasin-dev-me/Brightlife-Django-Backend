# Membership API - Frontend Integration Guide

**Backend Base URL**: `http://localhost:8000/api/membership/`  
**Production**: Update to your deployed backend URL

---

## 📡 API Endpoint

### Submit Membership Application

**Endpoint**: `POST /api/membership/applications/`  
**Authentication**: Not required (public endpoint)  
**Content-Type**: `multipart/form-data`

---

## 📤 Request Format

### TypeScript Interface (matches your MembershipFormData)

```typescript
interface MembershipFormData {
  // Step 1: Personal Information
  membershipType: 'individual' | 'family' | 'corporate';
  firstName: string;
  middleName?: string;
  lastName: string;
  dateOfBirth: string; // Format: YYYY-MM-DD
  gender: 'male' | 'female' | 'other';
  maritalStatus: 'single' | 'married' | 'divorced' | 'widowed';
  
  // Contact Information
  mobileNumber: string;
  email: string;
  emergencyContactName: string;
  emergencyContactNumber: string;
  
  // Identification
  nidNumber: string;
  passportNumber?: string;
  
  // Occupation
  occupation: string;
  organizationName?: string;
  monthlyIncome?: number;
  
  // Family Details
  spouseName?: string;
  numberOfChildren: number;
  fatherName: string;
  motherName: string;
  
  // Files - Step 1
  photo: File;
  ageProof: File;
  drivingLicense?: File;
  
  // Step 2: Address
  presentAddress: string;
  permanentAddress: string;
  
  // Step 3: Nominees (array of 1-3)
  nominees: Nominee[];
  
  // Step 4: Physical Measurements
  weight: number; // in kg
  height: number; // in cm
  bloodGroup: 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-';
  surgeryHistory?: string;
  medicalRecords?: File;
  prescription?: File;
  
  // Declaration
  termsAccepted: boolean;
}

interface Nominee {
  name: string;
  relationship: 'spouse' | 'father' | 'mother' | 'son' | 'daughter' | 'brother' | 'sister' | 'other';
  mobileNumber: string;
  nidNumber: string;
  dateOfBirth: string; // Format: YYYY-MM-DD
  sharePercentage: number; // Total must be 100 across all nominees
  idProof: File;
}
```

---

## 🔧 Frontend Implementation Example

### Using Fetch API

```typescript
async function submitMembershipApplication(formData: MembershipFormData) {
  const formDataToSend = new FormData();
  
  // Add all text fields
  formDataToSend.append('membership_type', formData.membershipType);
  formDataToSend.append('first_name', formData.firstName);
  formDataToSend.append('middle_name', formData.middleName || '');
  formDataToSend.append('last_name', formData.lastName);
  formDataToSend.append('date_of_birth', formData.dateOfBirth);
  formDataToSend.append('gender', formData.gender);
  formDataToSend.append('marital_status', formData.maritalStatus);
  formDataToSend.append('mobile_number', formData.mobileNumber);
  formDataToSend.append('email', formData.email);
  formDataToSend.append('emergency_contact_name', formData.emergencyContactName);
  formDataToSend.append('emergency_contact_number', formData.emergencyContactNumber);
  formDataToSend.append('nid_number', formData.nidNumber);
  formDataToSend.append('passport_number', formData.passportNumber || '');
  formDataToSend.append('occupation', formData.occupation);
  formDataToSend.append('organization_name', formData.organizationName || '');
  formDataToSend.append('monthly_income', formData.monthlyIncome?.toString() || '');
  formDataToSend.append('spouse_name', formData.spouseName || '');
  formDataToSend.append('number_of_children', formData.numberOfChildren.toString());
  formDataToSend.append('father_name', formData.fatherName);
  formDataToSend.append('mother_name', formData.motherName);
  formDataToSend.append('present_address', formData.presentAddress);
  formDataToSend.append('permanent_address', formData.permanentAddress);
  formDataToSend.append('weight', formData.weight.toString());
  formDataToSend.append('height', formData.height.toString());
  formDataToSend.append('blood_group', formData.bloodGroup);
  formDataToSend.append('surgery_history', formData.surgeryHistory || '');
  formDataToSend.append('terms_accepted', formData.termsAccepted.toString());
  
  // Add file uploads
  formDataToSend.append('photo', formData.photo);
  formDataToSend.append('age_proof', formData.ageProof);
  if (formData.drivingLicense) {
    formDataToSend.append('driving_license', formData.drivingLicense);
  }
  if (formData.medicalRecords) {
    formDataToSend.append('medical_records', formData.medicalRecords);
  }
  if (formData.prescription) {
    formDataToSend.append('prescription', formData.prescription);
  }
  
  // Add nominees (as JSON string)
  const nomineesData = formData.nominees.map(nominee => {
    const nomineeFormData = new FormData();
    nomineeFormData.append('name', nominee.name);
    nomineeFormData.append('relationship', nominee.relationship);
    nomineeFormData.append('mobile_number', nominee.mobileNumber);
    nomineeFormData.append('nid_number', nominee.nidNumber);
    nomineeFormData.append('date_of_birth', nominee.dateOfBirth);
    nomineeFormData.append('share_percentage', nominee.sharePercentage.toString());
    nomineeFormData.append('id_proof', nominee.idProof);
    return nomineeFormData;
  });
  
  // Serialize nominees for multipart upload
  formData.nominees.forEach((nominee, index) => {
    formDataToSend.append(`nominees[${index}]name`, nominee.name);
    formDataToSend.append(`nominees[${index}]relationship`, nominee.relationship);
    formDataToSend.append(`nominees[${index}]mobile_number`, nominee.mobileNumber);
    formDataToSend.append(`nominees[${index}]nid_number`, nominee.nidNumber);
    formDataToSend.append(`nominees[${index}]date_of_birth`, nominee.dateOfBirth);
    formDataToSend.append(`nominees[${index}]share_percentage`, nominee.sharePercentage.toString());
    formDataToSend.append(`nominees[${index}]id_proof`, nominee.idProof);
  });
  
  try {
    const response = await fetch('http://localhost:8000/api/membership/applications/', {
      method: 'POST',
      body: formDataToSend,
      // DO NOT set Content-Type header - browser will set it automatically with boundary
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Proposal Number:', result.data.proposal_number);
      return result.data;
    } else {
      throw new Error(result.message || 'Submission failed');
    }
  } catch (error) {
    console.error('Error submitting application:', error);
    throw error;
  }
}
```

---

## 📥 Response Format

### Success Response (201 Created)

```json
{
  "success": true,
  "message": "Application submitted successfully",
  "data": {
    "proposal_number": "BL-202511-0001",
    "id": "uuid-here",
    "status": "pending"
  }
}
```

### Error Response (400 Bad Request)

```json
{
  "success": false,
  "message": "Failed to submit application",
  "errors": {
    "nid_number": ["An application with this NID number already exists"],
    "nominees": ["Total share percentage must be 100%. Current total: 75%"],
    "photo": ["Photo size cannot exceed 5MB"]
  }
}
```

---

## ✅ Validation Rules

### Field Validations

1. **Nominees Share Percentage**:
   - Must total exactly 100%
   - Each nominee: 0-100%

2. **Age Requirement**:
   - Individual membership: Must be 18+ years old
   - Family/Corporate: No age restriction

3. **File Uploads**:
   - Max size: 5MB per file
   - Photo: JPG, JPEG, PNG only
   - Documents: PDF, JPG, JPEG, PNG

4. **Unique Fields**:
   - NID number must be unique

5. **Required Fields**:
   - All fields marked as required in TypeScript interface
   - `termsAccepted` must be `true`

---

## 🎯 Field Naming Convention

**Frontend (camelCase)** → **Backend (snake_case)**

| Frontend | Backend |
|----------|---------|
| `membershipType` | `membership_type` |
| `firstName` | `first_name` |
| `dateOfBirth` | `date_of_birth` |
| `mobileNumber` | `mobile_number` |
| `emergencyContactName` | `emergency_contact_name` |
| `nidNumber` | `nid_number` |
| `passportNumber` | `passport_number` |
| `organizationName` | `organization_name` |
| `monthlyIncome` | `monthly_income` |
| `spouseName` | `spouse_name` |
| `numberOfChildren` | `number_of_children` |
| `fatherName` | `father_name` |
| `motherName` | `mother_name` |
| `presentAddress` | `present_address` |
| `permanentAddress` | `permanent_address` |
| `bloodGroup` | `blood_group` |
| `surgeryHistory` | `surgery_history` |
| `ageProof` | `age_proof` |
| `drivingLicense` | `driving_license` |
| `medicalRecords` | `medical_records` |
| `termsAccepted` | `terms_accepted` |

**Nominees**:
| Frontend | Backend |
|----------|---------|
| `name` | `name` |
| `relationship` | `relationship` |
| `mobileNumber` | `mobile_number` |
| `nidNumber` | `nid_number` |
| `dateOfBirth` | `date_of_birth` |
| `sharePercentage` | `share_percentage` |
| `idProof` | `id_proof` |

---

## 🔄 Step-by-Step Integration

### 1. Update `.env.local` in Frontend

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK_API=false
```

### 2. Create API Service File

```typescript
// src/services/membershipApi.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function submitMembership(data: MembershipFormData) {
  // Implementation as shown above
}
```

### 3. Update Form Submission Handler

```typescript
// src/components/MembershipForm.tsx
const handleSubmit = async (formData: MembershipFormData) => {
  setIsSubmitting(true);
  try {
    const result = await submitMembership(formData);
    
    // Show success message
    alert(`Application submitted! Proposal Number: ${result.proposal_number}`);
    
    // Navigate to success page
    navigate(`/application/success/${result.id}`);
  } catch (error) {
    // Handle errors
    alert('Failed to submit application. Please try again.');
  } finally {
    setIsSubmitting(false);
  }
};
```

---

## 🧪 Testing Checklist

- [ ] Form submits with all required fields
- [ ] File uploads work (photo, documents)
- [ ] Nominee share percentage validation (must be 100%)
- [ ] Age validation (18+ for individual)
- [ ] Duplicate NID detection
- [ ] Success message shows proposal number
- [ ] Error messages display properly
- [ ] Loading state during submission
- [ ] Network error handling

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Error
**Error**: `Access to fetch at 'http://localhost:8000/api/membership/applications/' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solution**: Ensure backend `.env` includes:
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Issue 2: File Upload Fails
**Error**: `413 Request Entity Too Large` or `File size cannot exceed 5MB`

**Solution**: 
- Check file size < 5MB
- Ensure correct file extensions
- Verify `Content-Type: multipart/form-data` is set

### Issue 3: Nominee Share Percentage Error
**Error**: `Total share percentage must be 100%`

**Solution**: Ensure all nominees' `sharePercentage` values add up to exactly 100.

### Issue 4: Network Error
**Error**: `Failed to fetch` or connection refused

**Solution**:
- Ensure Django dev server is running: `python manage.py runserver`
- Check backend URL is correct in `.env.local`
- Verify PostgreSQL is running

---

## 📞 Support

For backend issues, check:
- Django logs in terminal
- `MEMBERSHIP_IMPLEMENTATION.md` for setup instructions
- Admin panel at `http://localhost:8000/admin/`
- API docs at `http://localhost:8000/api/schema/swagger-ui/`

---

**Backend API is ready for integration!** 🚀
