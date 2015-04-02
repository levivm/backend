BEGIN;
DROP TABLE "corsheaders_corsmodel";

COMMIT;
BEGIN;
DROP TABLE "activities_review";
DROP TABLE "activities_session";
DROP TABLE "activities_chronogram";
DROP TABLE "activities_activityphoto";
ALTER TABLE "activities_activity_instructors" DROP CONSTRAINT "activity_id_refs_id_1aa031ce";
ALTER TABLE "activities_activity_tags" DROP CONSTRAINT "activity_id_refs_id_e4b04d4b";
DROP TABLE "activities_activity";
DROP TABLE "activities_activity_instructors";
DROP TABLE "activities_activity_tags";
DROP TABLE "activities_tags";
DROP TABLE "activities_subcategory";
DROP TABLE "activities_category";

COMMIT;
BEGIN;
DROP TABLE "locations_location";
DROP TABLE "locations_city";

COMMIT;
BEGIN;
DROP TABLE "users_userprofile";

COMMIT;
BEGIN;
DROP TABLE "organizers_instructor";
DROP TABLE "organizers_organizer";

COMMIT;
BEGIN;
DROP TABLE "students_assistant";
DROP TABLE "students_student";

COMMIT;
