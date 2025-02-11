"""
Utility module holding surface generation related functions.
"""
import uuid
from pathlib import Path
from typing import Dict, List

from lapy import TriaMesh

from .utils.utils import run_shell_command


def create_cereb_surface(
    subject_dir: Path, destination: Path, indices: List[int]
) -> Path:
    

    cerebseg_path = subject_dir / "mri/cerebellum.CerebNet.nii.gz"
    norm_path = subject_dir / "mri/norm.mgz"
    temp_name = "temp/cereb.{uid}".format(uid=uuid.uuid4())
    indices_mask = destination / f"{temp_name}.mgz"
    # binarize on selected labels (creates temp indices_mask)
    # always binarize first, otherwise pretess may scale aseg if labels are
    # larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
    binarize_template = "mri_binarize --i {source} --match {match} --o {destination}"
    binarize_command = binarize_template.format(
        source=cerebseg_path, match=" ".join(indices), destination=indices_mask
    )
    run_shell_command(binarize_command)

    label_value = "1"
    # if norm exist, fix label (pretess)
    if norm_path.is_file():
        pretess_template = (
            "mri_pretess {source} {label_value} {norm_path} {destination}"
        )
        pretess_command = pretess_template.format(
            source=indices_mask,
            label_value=label_value,
            norm_path=norm_path,
            destination=indices_mask,
        )
        run_shell_command(pretess_command)

    # runs marching cube to extract surface
    surface_name = "{name}.surf".format(name=temp_name)
    surface_path = destination / surface_name
    extraction_template = "mri_mc {source} {label_value} {destination}"
    extraction_command = extraction_template.format(
        source=indices_mask, label_value=label_value, destination=surface_path
    )
    run_shell_command(extraction_command)

    # convert to vtk
    relative_path = "surfaces/cereb.final.{indices}.vtk".format(
        indices="_".join(indices)
    )
    conversion_destination = destination / relative_path
    conversion_template = "mris_convert {source} {destination}"
    conversion_command = conversion_template.format(
        source=surface_path, destination=conversion_destination
    )
    run_shell_command(conversion_command)

    return conversion_destination


def create_aseg_surface(
    subject_dir: Path, destination: Path, indices: List[int]
) -> Path:
    """
    Generate a surface from the aseg and label files.

    Parameters
    ----------
    subject_dir : Path
        Path to the subject's directory.
    destination : Path
        Path to the destination directory where the surface will be saved.
    indices : List[int]
        List of label indices to include in the surface generation.

    Returns
    -------
    Path
        Path to the generated surface in VTK format.
    """
    aseg_path = subject_dir / "mri/aseg.mgz"
    norm_path = subject_dir / "mri/norm.mgz"
    temp_name = "temp/aseg.{uid}".format(uid=uuid.uuid4())
    indices_mask = destination / f"{temp_name}.mgz"
    # binarize on selected labels (creates temp indices_mask)
    # always binarize first, otherwise pretess may scale aseg if labels are
    # larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
    binarize_template = "mri_binarize --i {source} --match {match} --o {destination}"
    binarize_command = binarize_template.format(
        source=aseg_path, match=" ".join(indices), destination=indices_mask
    )
    run_shell_command(binarize_command)

    label_value = "1"
    # if norm exist, fix label (pretess)
    if norm_path.is_file():
        pretess_template = (
            "mri_pretess {source} {label_value} {norm_path} {destination}"
        )
        pretess_command = pretess_template.format(
            source=indices_mask,
            label_value=label_value,
            norm_path=norm_path,
            destination=indices_mask,
        )
        run_shell_command(pretess_command)

    # runs marching cube to extract surface
    surface_name = "{name}.surf".format(name=temp_name)
    surface_path = destination / surface_name
    extraction_template = "mri_mc {source} {label_value} {destination}"
    extraction_command = extraction_template.format(
        source=indices_mask, label_value=label_value, destination=surface_path
    )
    run_shell_command(extraction_command)

    # convert to vtk
    relative_path = "surfaces/aseg.final.{indices}.vtk".format(
        indices="_".join(indices)
    )
    conversion_destination = destination / relative_path
    conversion_template = "mris_convert {source} {destination}"
    conversion_command = conversion_template.format(
        source=surface_path, destination=conversion_destination
    )
    run_shell_command(conversion_command)

    return conversion_destination


## Add functionality for cerebellum 

def create_cereb_surfaces(subject_dir: Path, destination: Path) -> Dict[str, Path]:
   
    cereb_labels = {
        #'Cbm_Left-Cerebellum-White-Matter': ['7'],
        #'Cbm_Left-Cerebellum-Cortex': ['8'],
        #'Cbm_Right-Cerebellum-White-Matter': ['46'],
        #'Cbm_Right-Cerebellum-Cortex': ['47'],
        'Cbm_Left_I_IV': ['601'],
        'Cbm_Right_I_IV': ['602'],
        'Cbm_Left_V': ['603'],
        'Cbm_Right_V': ['604'],
        'Cbm_Left_VI': ['605'],
        'Cbm_Vermis_VI': ['606'],
        'Cbm_Right_VI': ['607'],
        'Cbm_Left_CrusI': ['608'],
        'Cbm_Right_CrusI': ['610'],
        'Cbm_Left_CrusII': ['611'],
        'Cbm_Right_CrusII': ['613'],
        'Cbm_Left_VIIb': ['614'],
        'Cbm_Right_VIIb': ['616'],
        'Cbm_Left_VIIIa': ['617'],
        'Cbm_Right_VIIIa': ['619'],
        'Cbm_Left_VIIIb': ['620'],
        'Cbm_Right_VIIIb': ['622'],
        'Cbm_Left_IX': ['623'],
        'Cbm_Vermis_IX': ['624'],
        'Cbm_Right_IX': ['625'],
        'Cbm_Left_X': ['626'],
        'Cbm_Vermis_X': ['627'],
        'Cbm_Right_X': ['628'],
        'Cbm_Vermis_VII': ['630'],
        'Cbm_Vermis_VIII': ['631'],
        'Cbm_Vermis': ['631', '630', '627', '624', '606'],
    }

    return {
        label: create_cereb_surface(subject_dir, destination, indices)
        for label, indices in cereb_labels.items()
    }



def create_aseg_surfaces(subject_dir: Path, destination: Path) -> Dict[str, Path]:
    # Define aseg labels

    # combined and individual aseg labels:
    # - Left  Striatum: left  Caudate + Putamen + Accumbens
    # - Right Striatum: right Caudate + Putamen + Accumbens
    # - CorpusCallosum: 5 subregions combined
    # - Cerebellum: brainstem + (left+right) cerebellum WM and GM
    # - Ventricles: (left+right) lat.vent + inf.lat.vent + choroidplexus + 3rdVent + CSF
    # - Lateral-Ventricle: lat.vent + inf.lat.vent + choroidplexus
    # - 3rd-Ventricle: 3rd-Ventricle + CSF

    aseg_labels = {
        "CorpusCallosum": ["251", "252", "253", "254", "255"],
        "Cerebellum": ["7", "8", "16", "46", "47"],
        "Ventricles": ["4", "5", "14", "24", "31", "43", "44", "63"],
        "3rd-Ventricle": ["14", "24"],
        "4th-Ventricle": ["15"],
        "Brain-Stem": ["16"],
        "Left-Striatum": ["11", "12", "26"],
        "Left-Lateral-Ventricle": ["4", "5", "31"],
        "Left-Cerebellum-White-Matter": ["7"],
        "Left-Cerebellum-Cortex": ["8"],
        "Left-Thalamus-Proper": ["10"],
        "Left-Caudate": ["11"],
        "Left-Putamen": ["12"],
        "Left-Pallidum": ["13"],
        "Left-Hippocampus": ["17"],
        "Left-Amygdala": ["18"],
        "Left-Accumbens-area": ["26"],
        "Left-VentralDC": ["28"],
        "Right-Striatum": ["50", "51", "58"],
        "Right-Lateral-Ventricle": ["43", "44", "63"],
        "Right-Cerebellum-White-Matter": ["46"],
        "Right-Cerebellum-Cortex": ["47"],
        "Right-Thalamus-Proper": ["49"],
        "Right-Caudate": ["50"],
        "Right-Putamen": ["51"],
        "Right-Pallidum": ["52"],
        "Right-Hippocampus": ["53"],
        "Right-Amygdala": ["54"],
        "Right-Accumbens-area": ["58"],
        "Right-VentralDC": ["60"],
    }
    return {
        label: create_aseg_surface(subject_dir, destination, indices)
        for label, indices in aseg_labels.items()
    }


def create_cortical_surfaces(subject_dir: Path, destination: Path) -> Dict[str, Path]:
    cortical_labels = {
        "lh-white-2d": "lh.white",
        "rh-white-2d": "rh.white",
        "lh-pial-2d": "lh.pial",
        "rh-pial-2d": "rh.pial",
    }
    return {
        label: surf_to_vtk(
            subject_dir / "surf" / name,
            destination / "surfaces" / f"{name}.vtk",
        )
        for label, name in cortical_labels.items()
    }


def create_surfaces(
    subject_dir: Path, destination: Path, skip_cortex: bool = False, skip_cerebellum: bool = False
) -> Dict[str, Path]:
    surfaces = create_aseg_surfaces(subject_dir, destination)
    if not skip_cerebellum:
        surfaces.update(create_cereb_surfaces(subject_dir, destination))
    if not skip_cortex:
        cortical_surfaces = create_cortical_surfaces(subject_dir, destination)
        surfaces.update(cortical_surfaces)
    return surfaces


def read_vtk(path: Path):
    try:
        triangular_mesh = TriaMesh.read_vtk(path)
    except Exception:
        message = "Failed to read VTK from the following path: {path}!".format(
            path=path
        )
        raise RuntimeError(message)
    else:
        if triangular_mesh is None:
            message = "Failed to read VTK from the following path: {path}!".format(
                path=path
            )
            raise RuntimeError(message)
        return triangular_mesh


def surf_to_vtk(source: Path, destination: Path) -> Path:
    """
    Converted a FreeSurfer *.surf* file to *.vtk*.

    Parameters
    ----------
    source : Path
        FreeSurfer *.surf* file.
    destination : Path
        Equivalent *.vtk* file.

    Returns
    -------
    Path
        Resulting *.vtk* file.
    """
    TriaMesh.read_fssurf(source).write_vtk(destination)
    return destination
