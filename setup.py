from setuptools import setup, find_packages

setup(
    name="stactools-pointcloud",
    version="0.1.0",
    description="STAC plugin for point cloud data",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "stactools",
        "pdal",
    ],
    entry_points={
        "stactools.plugins": [
            "pointcloud=stactools.pointcloud",
        ],
    },
)