# Package Management Guide

## 📦 Installing New Packages

### ✅ **Method 1: Manual Addition (Recommended)**

This preserves your smart version constraints and conditional logic:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install the package
pip install <package-name> --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# 3. Check installed version
pip show <package-name>

# 4. Manually add to requirements.txt
# Open requirements.txt and add: <package-name>>=<version>
```

**Example: Installing Pillow**
```bash
pip install pillow --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
# Then add to requirements.txt: pillow>=12.0.0
```

---

### 🔄 **Method 2: pip freeze (Use with Caution)**

This captures ALL packages with exact versions:

```bash
pip freeze > requirements.txt
```

**⚠️ Problems with this approach:**

1. **Overwrites your smart versioning:**
   - Before: `Django>=5.0.6,<5.2` (flexible)
   - After: `Django==5.1.13` (pinned)

2. **Removes conditional logic:**
   - Before: `psycopg2-binary>=2.9.9; python_version < '3.13'`
   - After: Just `psycopg==3.2.11` (no conditions)

3. **Includes ALL sub-dependencies:**
   - Your file: 14 lines (core packages)
   - After freeze: 35+ lines (everything)

**When to use it:**
- For production deployments where you want exact reproducibility
- Create a separate `requirements-freeze.txt` for this purpose

---

## 📋 **Current requirements.txt Comparison**

### Your Smart requirements.txt (14 lines)
```txt
Django>=5.0.6,<5.2                          # Flexible version range
djangorestframework>=3.15.1
celery>=5.3.4
redis>=5.0.1
psycopg2-binary>=2.9.9; python_version < '3.13'  # Conditional!
psycopg[binary]>=3.1.0; python_version >= '3.13'
gunicorn>=21.2.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
python-dotenv>=1.0.0
feedparser>=6.0.11
requests>=2.31.0
django-cors-headers>=4.3.1
pillow>=12.0.0
```

### After pip freeze (35+ lines)
```txt
amqp==5.3.1                                 # Sub-dependency (not needed)
asgiref==3.10.0                             # Sub-dependency (not needed)
billiard==4.2.2                             # Sub-dependency (not needed)
celery==5.5.3                               # Pinned version
certifi==2025.10.5                          # Sub-dependency (not needed)
charset-normalizer==3.4.4                   # Sub-dependency (not needed)
click==8.3.0                                # Sub-dependency (not needed)
click-didyoumean==0.3.1                     # Sub-dependency (not needed)
... and 27 more lines
```

---

## 🎯 **Recommended Workflow**

### For Development (Daily Use)

```bash
# Install new package
pip install <package> --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Manually add to requirements.txt
echo "<package>>=<version>" >> requirements.txt
```

### For Production (Exact Versions)

Create a separate frozen requirements file:

```bash
# Generate frozen versions
pip freeze > requirements-prod.txt

# In production, use:
pip install -r requirements-prod.txt
```

---

## 🔍 **Version Specifiers Explained**

| Specifier | Meaning | Example |
|-----------|---------|---------|
| `==` | Exact version | `Django==5.1.13` |
| `>=` | Greater or equal | `Django>=5.0.6` |
| `<` | Less than | `Django<5.2` |
| `>=,<` | Range | `Django>=5.0.6,<5.2` |
| `~=` | Compatible release | `Django~=5.1.0` (5.1.x) |

**Recommendation:** Use `>=<version>` for flexibility with security updates.

---

## 🛠️ **Common Package Management Commands**

```bash
# List installed packages
pip list

# Show package details
pip show <package-name>

# Check for outdated packages
pip list --outdated

# Upgrade a package
pip install --upgrade <package-name> --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Uninstall a package
pip uninstall <package-name>

# Install from requirements.txt
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Show dependency tree
pip show <package-name>
```

---

## 📝 **Example: Adding Multiple Packages**

Let's say you need to add pandas, numpy, and matplotlib:

```bash
# 1. Install them
pip install pandas numpy matplotlib --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# 2. Check versions
pip show pandas numpy matplotlib

# 3. Manually add to requirements.txt:
# pandas>=2.0.0
# numpy>=1.24.0
# matplotlib>=3.7.0
```

Edit `requirements.txt`:
```txt
Django>=5.0.6,<5.2
djangorestframework>=3.15.1
celery>=5.3.4
redis>=5.0.1
psycopg2-binary>=2.9.9; python_version < '3.13'
psycopg[binary]>=3.1.0; python_version >= '3.13'
gunicorn>=21.2.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
python-dotenv>=1.0.0
feedparser>=6.0.11
requests>=2.31.0
django-cors-headers>=4.3.1
pillow>=12.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
```

---

## 🚨 **Troubleshooting**

### Problem: SSL Certificate Errors

**Solution:** Always use the trusted-host flags:
```bash
--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### Problem: Package Conflicts

**Solution:** Check which packages depend on conflicting versions:
```bash
pip show <package-name>
```

### Problem: Can't Install Package

**Solution:** Check if it supports Python 3.13:
```bash
# Visit PyPI page: https://pypi.org/project/<package-name>/
# Check "Programming Language :: Python :: 3.13"
```

---

## 🔄 **Creating Aliases (Optional)**

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Django/Python aliases
alias pipi='pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org'
alias activate='source venv/bin/activate'
alias runserver='python manage.py runserver'
alias shell='python manage.py shell'
alias migrate='python manage.py migrate'
alias makemigrations='python manage.py makemigrations'
```

Then you can just use:
```bash
pipi pandas  # Instead of the long command
```

---

## ✅ **Best Practices Summary**

1. ✅ **Always activate venv first**: `source venv/bin/activate`
2. ✅ **Use manual addition** for requirements.txt
3. ✅ **Use flexible version ranges**: `>=` not `==`
4. ✅ **Keep requirements.txt clean**: Only top-level dependencies
5. ✅ **Use pip freeze for production**: Create `requirements-prod.txt`
6. ✅ **Test after installing**: Run `python manage.py check`
7. ✅ **Commit requirements.txt**: Track changes in git

---

## 📚 **Further Reading**

- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Version Specifiers](https://peps.python.org/pep-0440/#version-specifiers)
- [Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

---

*Last updated: October 19, 2025*

