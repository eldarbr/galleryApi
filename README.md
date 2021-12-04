# galleryApi
### API system. An interface to operate with database.

Part of backend code for gallery project
<hr> 

#### Client requests: 
All client requests must be GET method and should be sent to **host/client/<task\>**, where task is in list:
- *photo* - photo by id, requested photo *id* is an argument
- *category* - category by label (id or alias), requested category *label* is an argument
- *photos_of_category* - photos that correspond to the category, category *id* is an argument
- *categories_of_photo* - categories that correspond to the photo, photo *id* is an argument
- *index* - photos index
- *categories_index* - categories index

<hr>

#### Master requests
All master requests must be POST method and its destination should match the template:
**host/master/<task\>/<subject\>/<infra_subject\>**.
Supported requests:
- **host/master/insert/photo** - insert new photo into the database. Input data:
    - *name* - photo name
    - *description* - photo description (optional)
    - *timestamp* - photo timestamp (optional)
    - *hidden* - hidden flag (optional, default - false)


- **host/master/modify/photo** - modify photo in the database. Input data:
    - *id* - id of photo to modify
    - *name* - new photo name (optional)
    - *description* - new photo description (optional)
    - *timestamp* - new photo timestamp (optional)
    - *hidden* - new hidden flag (optional)


- **host/master/get/photo** - get photo from the database. Input data:
    - *id* - id of requested photo
    - *include_hidden* - if hidden photo is expected to be returned (optional, default - false)
    - *include_incomplete* - if incomplete photo is expected to be returned (optional, default - false)


- **host/master/index/photo** - get index of photos from the database. Input data:
    - *include_hidden* - if hidden photos are expected to be returned (optional, default - false)
    - *include_incomplete* - if incomplete photos are expected to be returned (optional, default - false)


- **host/master/insert/category** - insert new category into the database. Input data:
    - *name* - category name
    - *alias* - category alias
    - *description* - category description (optional)
    - *hidden* - hidden flag (optional, default - false)


- **host/master/modify/category** - modify category in the database. Input data:
    - *id* - id of category to modify
    - *name* - category name (optional)
    - *alias* - category alias (optional)
    - *description* - category description (optional)
    - *hidden* - hidden flag (optional, default - false)


- **host/master/get/category** - get category from the database. Input data:
    - *label* - _id or alias_ of requested category
    - *include_hidden* - hidden flag (optional, default - false)


- **host/master/index/category** - get index of categories from the database. Input data:
    - *include_hidden* - hidden flag (optional, default - false)


- **host/master/add/relation/photo** - add relations of photo with categories. Input data:
    - *photo_id* - id of photo
    - *category_ids_list* - list of corresponding categories


- **host/master/replace/relation/photo** - replace relations of photo with categories. Input data:
    - *photo_id* - id of photo
    - *category_ids_list* - list of corresponding categories


- **host/master/delete/relation/photo** - delete all relations of photo with categories. Input data:
    - *photo_id* - id of photo


- **host/master/get/relation/photo** - get list of categories by photo. Input data:
    - *photo_id* - id of photo
    - *include_hidden* - if hidden categories are expected to be returned (optional, default - false)


- **host/master/add/relation/category** - add relations of category with photos. Input data:
    - *category_id* - id of category
    - *category_ids_list* - list of corresponding categories


- **host/master/replace/relation/category** - replace relations of category with photos. Input data:
    - *category_id* - id of category
    - *category_ids_list* - list of corresponding categories


- **host/master/delete/relation/category** - delete all relations of category with photos. Input data:
    - *category_id* - id of category


- **host/master/get/relation/category** - get list of photos by category. Input data:
    - *category_id* - id of category
    - *include_hidden* - if hidden photos are expected to be returned (optional, default - false)
