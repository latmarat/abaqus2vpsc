Scripts for obtaining local deformation history from ABAQUS simulations of a deformation process (e.g. metal forming) for VPSC texture simulations.

- j2isoVelGradOut.for - UMAT subroutine that includes calculation of the velocity gradient tensor (material model - J2 plasticity with isotropic hardening, adopted from ['Writing UMAT'](http://imechanica.org/node/7576))

- abaqus2vpsc.py - Python script that extracts the velocity gradient tensor from the ABAQUS output database and writes its components to a text file in a format readable by VPSC.

- elasplas2umat.py - utility Python script that converts conventionally defined elastoplastic material in ABAQUS/CAE to a user material required for j2isoVelGradOut.for UMAT subroutine/

See more details in this [blog post](http://latmarat.github.io/blog/tutorials/abaqus2vpsc).
