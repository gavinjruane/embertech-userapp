-- This query will join a name and username with the role title from the role table.
-- Should look like this: | <name> | <username> | <role> |
--                        | Josh   | jgonz      | Admin  |
SELECT Users.name, Users.username, Roles.title FROM Users INNER JOIN Roles ON Users.role=Roles.id;
