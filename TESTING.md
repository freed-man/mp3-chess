# Testing Documentation — Chess Club

[← Back to README](README.md)

## Table of Contents
1. [**Automated Testing**](#automated-testing)
2. [**Code Validation**](#code-validation)
   - [Python](#python)
   - [HTML](#html)
   - [CSS](#css)
   - [JavaScript](#javascript)
3. [**Manual Testing**](#manual-testing)
   - [Feature Testing](#feature-testing)
   - [Authentication Testing](#authentication-testing)
   - [CRUD Testing](#crud-testing)
   - [Defensive Testing](#defensive-testing)
4. [**Responsive Design Testing**](#responsive-design-testing)
5. [**Browser Compatibility**](#browser-compatibility)
6. [**Lighthouse Testing**](#lighthouse-testing)
7. [**Known Bugs**](#known-bugs)

---

## Automated Testing

Automated unit tests were written using Django's built-in TestCase framework. Tests are run against a temporary SQLite database to avoid affecting production data.

**Running tests:**
```
python manage.py test
```

### Club App Tests

**test_forms.py:**
| Test | Description | Result |
|------|------------|--------|
| test_comment_form_valid | Form is valid with body field filled | ✅ Pass |
| test_comment_form_invalid | Form is invalid when body is empty | ✅ Pass |

**test_views.py:**
| Test | Description | Result |
|------|------------|--------|
| test_homepage_renders | Homepage returns status 200 | ✅ Pass |
| test_topic_detail_renders | Topic detail page returns status 200 with correct content | ✅ Pass |
| test_comment_submission | Logged in user can post a comment | ✅ Pass |

**test_models.py:**
| Test | Description | Result |
|------|------------|--------|
| test_topic_str | Topic __str__ returns the title | ✅ Pass |
| test_comment_str | Comment __str__ returns expected format | ✅ Pass |
| test_vote_str | Vote __str__ returns expected format | ✅ Pass |

### Profiles App Tests

**test_forms.py:**
| Test | Description | Result |
|------|------------|--------|
| test_profile_form_valid | Profile form is valid with correct data | ✅ Pass |
| test_game_form_valid | Game form is valid with all fields | ✅ Pass |
| test_game_form_invalid | Game form is invalid when fields are empty | ✅ Pass |

**test_views.py:**
| Test | Description | Result |
|------|------------|--------|
| test_profile_page_renders | Profile page returns status 200 | ✅ Pass |
| test_profile_edit_authenticated | Logged in user can edit own profile | ✅ Pass |
| test_log_game | Logged in user can log a game | ✅ Pass |

**test_models.py:**
| Test | Description | Result |
|------|------------|--------|
| test_profile_auto_creation | Profile is auto-created when User is created via signal | ✅ Pass |
| test_profile_str | Profile __str__ returns expected format | ✅ Pass |
| test_game_str | Game __str__ returns expected format | ✅ Pass |

### About App Tests

**test_forms.py:**
| Test | Description | Result |
|------|------------|--------|
| test_contact_form_valid | Contact form is valid with all fields | ✅ Pass |
| test_contact_form_name_required | Form is invalid without name | ✅ Pass |
| test_contact_form_email_required | Form is invalid without email | ✅ Pass |
| test_contact_form_message_required | Form is invalid without message | ✅ Pass |

**test_views.py:**
| Test | Description | Result |
|------|------------|--------|
| test_about_page_renders | About page returns status 200 | ✅ Pass |
| test_contact_form_submission | Contact form submits successfully | ✅ Pass |

<details>
  <summary>View automated test results screenshot</summary>
  <p>Add screenshot of terminal showing all tests passing here</p>
</details>

---

## Code Validation

### Python

All Python files were validated using the [CI Python Linter](https://pep8ci.herokuapp.com/). All files pass with no errors.

| File | Result |
|------|--------|
| club/models.py | ✅ No errors |
| club/views.py | ✅ No errors |
| club/urls.py | ✅ No errors |
| club/forms.py | ✅ No errors |
| club/admin.py | ✅ No errors |
| club/test_forms.py | ✅ No errors |
| club/test_views.py | ✅ No errors |
| club/test_models.py | ✅ No errors |
| profiles/models.py | ✅ No errors |
| profiles/views.py | ✅ No errors |
| profiles/urls.py | ✅ No errors |
| profiles/forms.py | ✅ No errors |
| profiles/admin.py | ✅ No errors |
| profiles/signals.py | ✅ No errors |
| profiles/test_forms.py | ✅ No errors |
| profiles/test_views.py | ✅ No errors |
| profiles/test_models.py | ✅ No errors |
| about/models.py | ✅ No errors |
| about/views.py | ✅ No errors |
| about/urls.py | ✅ No errors |
| about/forms.py | ✅ No errors |
| about/admin.py | ✅ No errors |
| about/test_forms.py | ✅ No errors |
| about/test_views.py | ✅ No errors |
| chess/settings.py | ✅ No errors |
| chess/urls.py | ✅ No errors |

<details>
  <summary>View Python validation screenshots</summary>
  <p>Add screenshots of CI Python Linter results here</p>
</details>

### HTML

All pages were validated using the [W3C HTML Validator](https://validator.w3.org/) by URL on the deployed site.

| Page | Result |
|------|--------|
| Homepage | ✅ No errors |
| Topic Detail | ✅ No errors |
| About | ✅ No errors |
| Profile | ✅ No errors |
| Login | ✅ No errors |
| Signup | ✅ No errors |
| Logout | ✅ No errors |
| Search Results | ✅ No errors |

<details>
  <summary>View HTML validation screenshots</summary>
  <p>Add screenshots of W3C results here</p>
</details>

### CSS

CSS was validated using the [W3C CSS Validator](https://jigsaw.w3.org/css-validator/). No errors found.

<details>
  <summary>View CSS validation screenshot</summary>
  <p>Add screenshot here</p>
</details>

### JavaScript

JavaScript was validated using [JSHint](https://jshint.com/) with ES6 configured. No errors found. One undefined variable (`bootstrap`) which is loaded externally from the Bootstrap CDN.

<details>
  <summary>View JavaScript validation screenshot</summary>
  <p>Add screenshot here</p>
</details>

---

## Manual Testing

### Feature Testing

| Feature | Action | Expected Result | Result |
|---------|--------|----------------|--------|
| Homepage | Load page | Topics displayed in cards with images, pagination works | ✅ Pass |
| Topic Detail | Click topic | Full article with image, votes, and comments displayed | ✅ Pass |
| Search | Enter keyword and search | Matching topics displayed, message if none found | ✅ Pass |
| About Page | Load page | Club info displayed, contact form collapses/expands | ✅ Pass |
| Contact Form | Submit form | Message saved, success alert shown, form resets | ✅ Pass |
| Auto-dismiss Alerts | Trigger any message | Alert fades out after 3 seconds | ✅ Pass |

### Authentication Testing

| Feature | Action | Expected Result | Result |
|---------|--------|----------------|--------|
| Register | Submit signup form | Account created, profile auto-created, redirected to home | ✅ Pass |
| Login | Submit login form | Logged in, success message, redirected | ✅ Pass |
| Login from article | Click login link on article | After login, redirected back to same article | ✅ Pass |
| Logout | Confirm logout | Logged out, success message | ✅ Pass |
| Show Password | Click show password button | Password field toggles between hidden and visible | ✅ Pass |

### CRUD Testing

**Comments:**

| Action | Expected Result | Result |
|--------|----------------|--------|
| Create | Comment appears below article, success message | ✅ Pass |
| Read | Comments displayed with author and date | ✅ Pass |
| Update | Edit button populates form, comment updates on save | ✅ Pass |
| Delete | Confirmation modal shown, comment removed on confirm | ✅ Pass |

**Games:**

| Action | Expected Result | Result |
|--------|----------------|--------|
| Create | Game logged, appears in game history with date picker | ✅ Pass |
| Read | Game history table shows opponent, date, result with colours | ✅ Pass |
| Update | Edit form pre-fills, game updates on save | ✅ Pass |
| Delete | Confirmation prompt, game removed | ✅ Pass |

**Profile:**

| Action | Expected Result | Result |
|--------|----------------|--------|
| Read | Profile displays photo, bio, skill level, stats | ✅ Pass |
| Update | Edit form pre-fills, profile updates including photo | ✅ Pass |
| Delete Account | Confirmation modal, account and all data removed | ✅ Pass |

**Voting:**

| Action | Expected Result | Result |
|--------|----------------|--------|
| Upvote | Vote count increases, button highlighted | ✅ Pass |
| Downvote | Vote count increases, button highlighted | ✅ Pass |
| Toggle off | Click same vote again, vote removed | ✅ Pass |
| Switch vote | Click opposite vote, switches from up to down or vice versa | ✅ Pass |

### Defensive Testing

| Test | Expected Result | Result |
|------|----------------|--------|
| Edit another user's profile | Error message, redirected | ✅ Pass |
| Edit another user's game | Error message, redirected | ✅ Pass |
| Delete another user's comment | Error message, not deleted | ✅ Pass |
| Access profile edit while logged out | Redirected to login | ✅ Pass |
| Access log game while logged out | Redirected to login | ✅ Pass |
| Vote while logged out | Vote buttons disabled, no action | ✅ Pass |
| Comment while logged out | "Log in to leave a comment" shown with link | ✅ Pass |
| Refresh after posting comment | No duplicate comment (POST redirect) | ✅ Pass |
| Refresh after submitting contact form | No duplicate submission (POST redirect) | ✅ Pass |

---

## Responsive Design Testing

The site was tested across multiple screen sizes to ensure proper layout and functionality.

| Device | Result |
|--------|--------|
| Desktop (1920x1080) | ✅ All layouts correct |
| Laptop (1366x768) | ✅ All layouts correct |
| Tablet (768x1024) | ✅ Cards stack correctly, navigation collapses |
| Mobile (375x667) | ✅ Single column layout, images stack properly, topic images appear above article on mobile |

<details>
  <summary>View responsive design screenshots</summary>
  <p>Add screenshots here</p>
</details>

---

## Browser Compatibility

| Browser | Result |
|---------|--------|
| Google Chrome | ✅ Full functionality |
| Mozilla Firefox | ✅ Full functionality |
| Microsoft Edge | ✅ Full functionality |
| Safari | ✅ Full functionality |

---

## Lighthouse Testing

Google Chrome Lighthouse was used to test performance, accessibility, best practices, and SEO.

<details>
  <summary>Desktop Results</summary>
  <p>Add Lighthouse desktop screenshot here</p>
</details>

<details>
  <summary>Mobile Results</summary>
  <p>Add Lighthouse mobile screenshot here</p>
</details>

---

## Known Bugs

- **Opponent name matching** — the clickable opponent feature in game history relies on the opponent name exactly matching a registered username. There is no autocomplete or dropdown, so users must type the username precisely for the link to work.
- **Info message on HTML validation** — W3C validator shows an info message about trailing slashes on void elements. This is a non-error informational notice and does not affect functionality.

---

[← Back to README](README.md)
