import math
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class DiffusionStrategy(ABC):
    """Abstract base class for diffusion strategies."""

    @abstractmethod
    def calculate(
        self,
        dt: float,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        nu: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Apply diffusion to the given positions and velocities.

           Parameters
           ----------
            dt: Time step for diffusion calculation
            x: Array of x-coordinates.
            y: Array of y-coordinates.
            u: Array of x-velocity components.
            v: Array of y-velocity components.
            nu: Diffusion coefficient.

        Returns
        -------
            Tuple of updated x and y positions after diffusion (xdif, ydif).
        """
        pass


class GradientDiffusion(DiffusionStrategy):
    """
    Diffusion based on spatial gradients of the velocity field.
    """

    def calculate(
        self,
        dt: float,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        nu: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Example dummy diffusion calculation using gradients of the velocity field.

        For unstructured grids, gradients are approximated using nearest-neighbor differences.
        """
        n = len(x)
        dudx = np.zeros(n)
        dudy = np.zeros(n)
        dvdx = np.zeros(n)
        dvdy = np.zeros(n)

        for i in range(n):
            distances = np.sqrt((x - x[i]) ** 2 + (y - y[i]) ** 2)
            if np.all(distances == 0):  # Only one point
                continue
            nearest_idx = np.argmin(distances + np.eye(n) * 1e10)
            dx = x[nearest_idx] - x[i]
            dy = y[nearest_idx] - y[i]
            if dx != 0 or dy != 0:
                scale = 1.0 / (dx**2 + dy**2 + 1e-10)
                dudx[i] = (u[nearest_idx] - u[i]) * dx * scale
                dudy[i] = (u[nearest_idx] - u[i]) * dy * scale
                dvdx[i] = (v[nearest_idx] - v[i]) * dx * scale
                dvdy[i] = (v[nearest_idx] - v[i]) * dy * scale

        # Diffusion terms: nu * Laplacian
        xdif = nu * (dudx + dvdy)
        ydif = nu * (dudy + dvdx)
        return xdif, ydif


class RandomDiffusion(DiffusionStrategy):
    """
    Random walk diffusion model.
    """

    def calculate(
        self,
        dt: float,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        nu: float,
    ) -> Tuple[float, float]:
        vel_mag = np.sqrt(u**2 + v**2)
        rndnr_mag = np.random.randn(*vel_mag.shape)
        mag_diff = np.abs(rndnr_mag * nu) * vel_mag
        rndnr_angle = np.random.rand(*vel_mag.shape)
        angle_diff = rndnr_angle * 2 * math.pi
        dx_diff = mag_diff * np.cos(angle_diff) * dt
        dy_diff = mag_diff * np.sin(angle_diff) * dt
        xdif = x + dx_diff
        ydif = y + dy_diff

        return xdif, ydif


class DiffusionCalculator:
    """
    Main class for calculating diffusion effects.
    """

    def __init__(self, strategy: DiffusionStrategy):
        """Initialize with a diffusion strategy.

        Parameters
        ----------
            strategy: DiffusionStrategy object to use
        """
        self._strategy = strategy

    @property
    def strategy(self) -> DiffusionStrategy:
        """
        Get the current diffusion strategy.
        """
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: DiffusionStrategy):
        """Change the diffusion strategy.

        Parameters
        ----------
            strategy: New DiffusionStrategy object to use
        """
        self._strategy = strategy

    def calc_diffusion(
        self,
        x: float,
        y: float,
        u: np.ndarray,
        v: np.ndarray,
        nu: float,
        dt: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate diffusion effect on position.

        Parameters
        ----------
            x: Current x position
            y: Current y position
            u: Velocity field x-component (2D array)
            v: Velocity field y-component (2D array)
            nu: Diffusion coefficient
            dt: Current time step

        Returns
        -------
            Tuple of (x_diffusion, y_diffusion) representing position changes
        """
        return self._strategy.calculate(dt, x, y, u, v, nu)
