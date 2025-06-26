#!/usr/bin/env python3
"""
Script para ejecutar tests con cobertura de código
Uso: python run_tests.py
"""

import os
import sys
import subprocess
import argparse

def install_requirements():
    """Instala las dependencias necesarias"""
    requirements = [
        'pygame',
        'coverage',
        'pytest',
        'pytest-cov'
    ]
    
    print("Instalando dependencias...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
            print(f"✓ {req} instalado")
        except subprocess.CalledProcessError:
            print(f"✗ Error instalando {req}")
            return False
    return True

def run_unittest_coverage():
    """Ejecuta tests usando unittest con coverage"""
    print("\n" + "="*60)
    print("EJECUTANDO TESTS CON UNITTEST + COVERAGE")
    print("="*60)
    
    # Comandos para ejecutar coverage
    commands = [
        # Ejecutar tests con coverage
        [sys.executable, '-m', 'coverage', 'run', '--source=.', 'test_game.py'],
        # Generar reporte en consola
        [sys.executable, '-m', 'coverage', 'report', '--show-missing'],
        # Generar reporte HTML
        [sys.executable, '-m', 'coverage', 'html']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"Error ejecutando: {' '.join(cmd)}")
                print(result.stderr)
                return False
        except FileNotFoundError:
            print(f"Error: No se encontró el comando {cmd[0]}")
            return False
    
    return True

def run_pytest_coverage():
    """Ejecuta tests usando pytest con coverage"""
    print("\n" + "="*60)
    print("EJECUTANDO TESTS CON PYTEST + COVERAGE")
    print("="*60)
    
    cmd = [
        sys.executable, '-m', 'pytest', 
        '--cov=game',  # Módulo a cubrir
        '--cov-report=html',  # Reporte HTML
        '--cov-report=term-missing',  # Reporte en terminal
        '--cov-fail-under=85',  # Fallar si cobertura < 85%
        'test_game.py',
        '-v'  # Verbose
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: pytest no encontrado")
        return False

def create_pytest_ini():
    """Crea archivo de configuración para pytest"""
    content = """[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --strict-config
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
"""
    
    with open('pytest.ini', 'w') as f:
        f.write(content)
    print("✓ Archivo pytest.ini creado")

def create_coverage_config():
    """Crea archivo de configuración para coverage"""
    content = """[run]
source = .
omit = 
    test_*.py
    setup.py
    venv/*
    env/*
    */venv/*
    */env/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\\bProtocol\\):
    @(abc\\.)?abstractmethod

[html]
directory = htmlcov
"""
    
    with open('.coveragerc', 'w') as f:
        f.write(content)
    print("✓ Archivo .coveragerc creado")

def main():
    parser = argparse.ArgumentParser(description='Ejecutar tests con cobertura')
    parser.add_argument('--install', action='store_true', 
                       help='Instalar dependencias')
    parser.add_argument('--method', choices=['unittest', 'pytest', 'both'], 
                       default='both', help='Método de testing a usar')
    parser.add_argument('--setup', action='store_true',
                       help='Crear archivos de configuración')
    
    args = parser.parse_args()
    
    if args.install:
        if not install_requirements():
            print("Error instalando dependencias")
            return 1
    
    if args.setup:
        create_pytest_ini()
        create_coverage_config()
        print("✓ Archivos de configuración creados")
    
    success = True
    
    if args.method in ['unittest', 'both']:
        success &= run_unittest_coverage()
    
    if args.method in ['pytest', 'both']:
        success &= run_pytest_coverage()
    
    if success:
        print("\n" + "="*60)
        print("✓ TESTS COMPLETADOS EXITOSAMENTE")
        print("✓ Revisa el reporte HTML en: htmlcov/index.html")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("✗ ALGUNOS TESTS FALLARON")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())