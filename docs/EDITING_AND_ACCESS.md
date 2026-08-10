# Editing and access

## Running website feedback

The single feedback thread is:

`https://github.com/antlerboy/PSTA/issues/2`

Anyone with a GitHub account who can see the public repository can add comments there. They do not need repository write access. This is the right place for rough observations, public wording that feels wrong, missing content, programme changes, partner changes, visual problems, and ideas for a later iteration.

The small white square at the bottom-right of the homepage opens this thread. `Alt+Shift+N` does the same thing.

## Publishing approved news

The structured **Publish a PSTA news item** issue form requires repository write access because submission automatically creates public website content. The automation checks the submitter's permission before it writes anything.

David and Natasa can therefore use two different levels of access:

- a normal GitHub account is enough to comment in the feedback thread;
- **Write** access is needed to use the automatic news-publishing form or edit website source files.

## Give David Mason and Natasa Sears write access

Open:

`https://github.com/antlerboy/PSTA/settings/access`

Then:

1. select **Add people**;
2. enter the person's GitHub username or the email address attached to their GitHub account;
3. send the invitation;
4. after they accept, set their repository role to **Write** if GitHub does not apply it automatically; and
5. ask them to sign in once and confirm they can see the issue templates.

Write access lets them publish approved news, edit files, open branches, and create pull requests. It does not give them access to account billing or unrelated repositories.

The repository owner should keep **Admin** access. There is no reason to give routine content editors Admin access.

## Safer editing pattern

For ordinary content changes:

- use the running feedback thread for notes;
- use the news form for approved news;
- use a branch and pull request for structural, design, policy, programme, or navigation changes; and
- let the Pages workflow test and deploy the merged result.

This keeps rough thinking, editorial decisions, and published material distinct without creating a separate content-management system.
