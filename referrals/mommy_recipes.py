from django.utils.timezone import utc
from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key, seq

from referrals.models import Referral, CouponType, Coupon, Redeem
from students.mommy_recipes import student


fake = Faker()

def date_with_utc(date):
    return date.replace(tzinfo=utc)

referral = Recipe(
    Referral,
    referred=foreign_key(student),
    referrer=foreign_key(student),
    ip_address=fake.ipv4,
)

coupon_type = Recipe(
    CouponType,
    name=seq('coupon'),
    amount=mommy.generators.gen_integer(min_int=100000, max_int=500000),
    type=mommy.generators.gen_from_choices(CouponType.TYPES),
)

coupon = Recipe(
    Coupon,
    coupon_type=foreign_key(coupon_type),
    valid_until=date_with_utc(fake.date_time_this_decade(before_now=False, after_now=True)),
)

redeem = Recipe(
    Redeem,
    student=foreign_key(student),
    coupon=foreign_key(coupon),
    used=fake.boolean,
)
