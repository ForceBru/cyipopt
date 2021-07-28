"""Test functionality of CyIpopt with/without optional SciPy dependency.

SciPy is an optional dependency of CyIpopt. CyIpopt needs to function without
SciPy installed, but also needs to provide the :func:`minimize_ipopt` function
which requires SciPy.

"""

import re
import sys

import numpy as np
import pytest

import cyipopt


@pytest.mark.skipif("scipy" in sys.modules,
                    reason="Test only valid if no Scipy available.")
def test_minimize_ipopt_import_error_if_no_scipy():
    """`minimize_ipopt` not callable without SciPy installed."""
    expected_error_msg = re.escape("Install SciPy to use the "
                                   "`minimize_ipopt` function.")
    with pytest.raises(ImportError, match=expected_error_msg):
        cyipopt.minimize_ipopt(None, None)


@pytest.mark.skipif("scipy" not in sys.modules,
                    reason="Test only valid if Scipy available.")
def test_minimize_ipopt_if_scipy():
    """If SciPy is installed `minimize_ipopt` works correctly."""
    from scipy.optimize import rosen, rosen_der
    x0 = [1.3, 0.7, 0.8, 1.9, 1.2]
    res = cyipopt.minimize_ipopt(rosen, x0, jac=rosen_der)
    assert isinstance(res, dict)
    assert np.isclose(res.get("fun"), 0.0)
    assert res.get("status") == 0
    assert res.get("success") is True
    np.testing.assert_allclose(res.get("x"), np.ones(5))


@pytest.mark.skipif("scipy" not in sys.modules,
                    reason="Test only valid if Scipy available.")
def test_minimize_ipopt_nojac_if_scipy():
    """`minimize_ipopt` works without Jacobian."""
    from scipy.optimize import rosen
    x0 = [1.3, 0.7, 0.8, 1.9, 1.2]
    options = {"tol": 1e-7}
    res = cyipopt.minimize_ipopt(rosen, x0, options=options)

    assert isinstance(res, dict)
    assert np.isclose(res.get("fun"), 0.0)
    assert res.get("status") == 0
    assert res.get("success") is True
    np.testing.assert_allclose(res.get("x"), np.ones(5), rtol=1e-5)


@pytest.mark.skipif("scipy" not in sys.modules,
                    reason="Test only valid if Scipy available.")
def test_minimize_ipopt_nojac_constraints_if_scipy():
    """ `minimize_ipopt` works without Jacobian and with constraints"""
    from scipy.optimize import rosen
    x0 = [1.3, 0.7, 0.8, 1.9, 1.2]
    constr = {"fun": lambda x: rosen(x) - 1.0, "type": "ineq"}
    res = cyipopt.minimize_ipopt(rosen, x0, constraints=constr)
    assert isinstance(res, dict)
    assert np.isclose(res.get("fun"), 1.0)
    assert res.get("status") == 0
    assert res.get("success") is True
    expected_res = np.array([1.001867, 0.99434067, 1.05070075, 1.17906312,
                             1.38103001])
    np.testing.assert_allclose(res.get("x"), expected_res)


@pytest.mark.skipif("scipy" not in sys.modules,
                    reason="Test only valid if Scipy available.")
def test_minimize_ipopt_jac_and_hessians_constraints_if_scipy():
    """`minimize_ipopt` works with objective gradient and Hessian 
       and constraint jacobians and Hessians."""
    from scipy.optimize import rosen, rosen_der, rosen_hess
    x0 = [1.3, 0.7, 0.8, 1.9, 1.2]
    constr = {"fun": lambda x: rosen(x) - 1.0, "type": "ineq",
              "jac": rosen_der, "hess": lambda x, v: rosen_hess(x) * v[0]}
    res = cyipopt.minimize_ipopt(rosen, x0, jac=rosen_der, hess=rosen_hess,
                                 constraints=constr)
    assert isinstance(res, dict)
    assert np.isclose(res.get("fun"), 1.0828541)
    assert res.get("status") == 0
    assert res.get("success") is True
    expected_res = np.array([1.09022019, 1.14568613, 1.30965199, 1.71962948,
                             2.90683532])
    np.testing.assert_allclose(res.get("x"), expected_res)


@pytest.mark.skipif("scipy" not in sys.modules,
                    reason="Test only valid if Scipy available.")
def test_minimize_ipopt_constraint_jac_true_if_scipy():
    """ `minimize_ipopt` works with objective gradient and Hessian 
         and constraint jacobians and Hessians"""
    from scipy.optimize import rosen, rosen_der
    x0 = [1.3, 0.7, 0.8, 1.9, 1.2]
    constr = {
        "fun": lambda x: (rosen(x) - 2.0, rosen_der(x)),
        "type": "ineq",
        "jac": True,
    }
    res = cyipopt.minimize_ipopt(rosen, x0,
                                 jac=rosen_der,
                                 constraints=constr)
    assert isinstance(res, dict)
    assert np.isclose(res.get("fun"), 2.0)
    assert res.get("status") == 0
    assert res.get("success") is True
    expected_res = np.array(
        [1.0040163, 0.9791639, 1.04011872, 1.18788545, 1.38059278])
    np.testing.assert_allclose(res.get("x"), expected_res)
