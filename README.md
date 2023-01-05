# An article management system

### Advance database course at IUST

### Technology stack: `python, elasticsearch`

![EER](https://github.com/mehransi/article-management-system/raw/master/EER.png)

---
### Instructions
1. `activate a python3 virtualenv`
2. ```shell
    pip install -r requirements.txt
    ```
3. ```shell
   ./manage.py migrate
   ```
4. ```shell
    ./manage.py initialize_documents
    ```
5. ```shell
    ./manage.py load_exports apps/account
    ./manage.py load_exports apps/article
    ```
6. ```shell
   ./manage.py runserver
    ```

