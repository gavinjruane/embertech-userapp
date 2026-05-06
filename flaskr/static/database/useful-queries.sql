-- This query will join a name and username with the role title from the role table.
-- Should look like this: | <name> | <username> | <role> |
--                        | Josh   | jgonz      | Admin  |
SELECT Users.name, Users.username, Roles.title FROM Users INNER JOIN Roles ON Users.role=Roles.id;


-- This query will get all users with the 'Standard' role.
SELECT Users.name, Users.username, Roles.title FROM Users INNER JOIN Roles ON Users.role=Roles.id
WHERE Roles.title='Standard';
