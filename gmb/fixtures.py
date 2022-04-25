
import random
import string
import hashlib
from datetime import datetime

from faker import Faker

from gmb.models import Locations, Accounts, Reviews, Collection, \
    Reviewer

fake = Faker()

STAR_RATING = {
    '0': 'STAR_RATING_UNSPECIFIED',
    '1': 'ONE',
    '2': 'TWO',
    '3': 'THREE',
    '4': 'FOUR',
    '5': 'FIVE'
}

def get_hash() -> str:
    options = string.digits + string.ascii_lowercase + string.ascii_uppercase
    values = []
    for i in list(range(1,33)):
        values.append(str(random.choice(options)))
    value = ''.join(values)
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

def fake_account() -> Accounts:
    name = 'accounts/' + get_hash()
    accountName = fake.name()
    primaryOwner = get_hash()
    type = 'PERSONAL'
    role = 'Some role'
    account = Accounts(name=name, accountName=accountName, primaryOwner=primaryOwner, role=role, type=type)
    account.save()
    return account

def random_accounts() -> list:
    items_gerados = []
    for i in list(range(1,33)):
        a = fake_account()
        items_gerados.append(a)
    return items_gerados

def random_locations() -> list:
    items_gerados = []
    for i in list(range(1,33)):
        account = fake_account()
        name = 'Negocio {}'.format(str(i))
        objeto = Locations(name=name, languageCode='pt-br', storeCode=get_hash(), title=name, account_id=account.id)
        objeto.save()
        items_gerados.append(objeto)
    return items_gerados

def random_reviewer():
    displayName = fake.name()
    profilePhotoUrl = '/url/photo/photo.jpg'
    isAnonymous = 'false'
    reviewer = Reviewer(displayName=displayName, isAnonymous=isAnonymous, profilePhotoUrl=profilePhotoUrl)
    reviewer.save()
    return reviewer


def random_reviews() -> list:
    locations = Locations.list()
    reviews_gerados = []
    for i, l in enumerate(locations):
        name = 'Review {}'.format(i)
        reviewId = i
        starRating = STAR_RATING[str(random.choice(list(range(0,6))))]
        location_id = l.id
        createTime = datetime.now().strftime('%Y-%m-%d')
        updateTime = datetime.now().strftime('%Y-%m-%d')
        comment = 'Lorem Ipsum dolor set atmet ' + str(i)
        reviewer = random_reviewer()
        r = Reviews(name=name, reviewId=reviewId, starRating=starRating, location_id=location_id, createTime=createTime, updateTime=updateTime, comment=comment, reviewer_id=reviewer.id)
        r.save()
        reviews_gerados.append(r)
    return reviews_gerados
