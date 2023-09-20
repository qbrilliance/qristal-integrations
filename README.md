# QB SDK - Integrations
---
### Important change announcement for Qristal users:

>
> **Qristal is moving to GitHub**
>
> [https://github.com/qbrilliance/qristal](https://github.com/qbrilliance/qristal)
>
> We are making this change to engage more effectively with the developer community.
>
>Please read the following information, as you will need to take action as soon as possible to minimise any potential impact to your development workflow.
>
> **When is the change happening?**
>
> Qristal is available [from GitHub](https://github.com/qbrilliance/) **now**.
>
> On **Friday, 20 October 2023**,  public access will be removed from the existing GitLab repository.
>

#### If I have cloned Qristal Integrations, how do I set the new GitHub repository as the `remote`?
```
git remote remove origin
git remote add origin https://github.com/qbrilliance/qristal-integrations.git
git fetch
git branch --set-upstream-to=origin/main main
```

#### If I have used Qristal Integrations as a git submodule of my project, how do I update this to use the new GitHub repository?
```
git rm your/project/path/to/Qristal-Integrations
git submodule add https://github.com/qbrilliance/qristal-integrations.git your/project/path/to/Qristal-Integrations
git submodule update --init --recursive
```

#### What will happen to my local repository if I don’t take any action?

Your local repository will no longer be in sync with newer releases of Qristal.

#### Who can I contact if I have questions about the change to GitHub?

Please raise any questions with:

Simon Yin (Developer Relations, <simon.y@quantum-brilliance.com>)



---

## Description
This is a collection of scripts and enhancements for Qristal to enable interoperability with other IDEs, workflow orchestrators, and high productivity technical software environments.

## Directory structure
- docker - contains build scripts for Docker containers
- jupyterlab
- nextflow
- tests
- theia
- vscode

## License
[Apache 2.0](LICENSE)
