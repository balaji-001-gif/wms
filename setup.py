from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="wms",
    version="1.0.0",
    description="Warehouse Management System for ERPNext v15+",
    author="Your Company",
    author_email="dev@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
