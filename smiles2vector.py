import csv
import networkx as nx
import numpy as np
from rdkit import Chem

folder = "./data_WS/"

"""
The following code will convert the SMILES format into onehot format
"""


# def atom_features(atom):
#     return np.array(one_of_k_encoding_unk(atom.GetSymbol(),
#                                           ['C', 'N', 'O', 'S', 'F', 'Si', 'P', 'Cl', 'Br', 'Mg', 'Na', 'Ca', 'Fe', 'As',
#                                            'Al', 'I', 'B', 'V', 'K', 'Tl', 'Yb', 'Sb', 'Sn', 'Ag', 'Pd', 'Co', 'Se',
#                                            'Ti', 'Zn', 'H', 'Li', 'Ge', 'Cu', 'Au', 'Ni', 'Cd', 'In', 'Mn', 'Zr', 'Cr',
#                                            'Pt', 'Hg', 'Pb', 'Unknown']) +
#                     one_of_k_encoding(atom.GetDegree(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
#                     one_of_k_encoding_unk(atom.GetTotalNumHs(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
#                     one_of_k_encoding_unk(atom.GetImplicitValence(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
#                     [atom.GetIsAromatic()])

def atom_features(atom):
    HYB_list = [Chem.rdchem.HybridizationType.S, Chem.rdchem.HybridizationType.SP,
                Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP3,
                Chem.rdchem.HybridizationType.SP3D, Chem.rdchem.HybridizationType.SP3D2,
                Chem.rdchem.HybridizationType.UNSPECIFIED, Chem.rdchem.HybridizationType.OTHER]
    return np.array(one_of_k_encoding_unk(atom.GetSymbol(),
                                          ['C', 'N', 'O', 'S', 'F', 'Si', 'P', 'Cl', 'Br', 'Mg', 'Na', 'Ca', 'Fe', 'As',
                                           'Al', 'I', 'B', 'V', 'K', 'Tl', 'Yb', 'Sb', 'Sn', 'Ag', 'Pd', 'Co', 'Se',
                                           'Ti', 'Zn', 'H', 'Li', 'Ge', 'Cu', 'Au', 'Ni', 'Cd', 'In', 'Mn', 'Zr', 'Cr',
                                           'Pt', 'Hg', 'Pb', 'Sm', 'Tc', 'Gd', 'Unknown']) +
                    one_of_k_encoding(atom.GetDegree(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetTotalNumHs(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetExplicitValence(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetImplicitValence(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding(atom.GetFormalCharge(), [-4, -3, -2, -1, 0, 1, 2, 3, 4]) +
                    one_of_k_encoding(atom.GetHybridization(), HYB_list) +
                    [atom.GetIsAromatic()])


def one_of_k_encoding(x, allowable_set):
    if x not in allowable_set:
        raise Exception("input {0} not in allowable set{1}:".format(x, allowable_set))
    return list(map(lambda s: x == s, allowable_set))


def one_of_k_encoding_unk(x, allowable_set):
    """Maps inputs not in the allowable set to the last element."""
    if x not in allowable_set:
        x = allowable_set[-1]
    # lambda 定义一个匿名函数
    # map 遍历allowable_set的每个元素，执行lambda函数，返回由函数返回值组成的列表
    return list(map(lambda s: x == s, allowable_set))


def smile_to_graph(smile):
    # 读取smile,smiles转换为分子对象，转为2D图
    # print(smile)
    mol = Chem.MolFromSmiles(smile)

    # print(type(mol))
    # 图的顶点数量
    c_size = mol.GetNumAtoms()

    features = []
    for atom in mol.GetAtoms():
        # 上个函数，独热编码格式
        feature = atom_features(atom)
        # 归一化？？？
        # features.append(feature / sum(feature))
        features.append(feature)

    features = np.array(features)

    # features = features / np.sum(features, 0)
    # features[np.isnan(features)] = 0

    edges = []
    edge_type = []
    for bond in mol.GetBonds():
        edges.append([bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()])
        edge_type.append(bond.GetBondTypeAsDouble())
    # 返回图形的有向表示，
    # 返回值：G –具有相同名称，相同节点且每个边（u，v，数据）由两个有向边（u，v，数据）和（v，u，数据）替换的有向图。
    g = nx.Graph(edges).to_directed()
    edge_index = []
    for e1, e2 in g.edges:
        edge_index.append([e1, e2])

    if not edge_index:
        edge_index = []
    else:
        edge_index = np.array(edge_index).transpose(1, 0)

    return c_size, features, edge_index, edge_type


def load_drug_smile(file):
    """
    :return: drug_dict {} 键值对为 name: 序号,
             drug_smile [] 所有drug的smile
             # smile_graph {} 键值对为 simle: graph
    """
    reader = csv.reader(open(file))
    # next(reader, None)

    drug_dict = {}
    drug_smile = []

    for item in reader:
        name = item[0]
        smile = item[1]
        # 除去重复的name，字典键值对为name-序号
        if name in drug_dict:
            pos = drug_dict[name]
        else:
            pos = len(drug_dict)
            drug_dict[name] = pos
        drug_smile.append(smile)
    """    
    # 将smile转化为图结构（内部再转化为独热编码）
    smile_graph = {}
    for smile in drug_smile:
        g = smile_to_graph(smile)
        smile_graph[smile] = g
    """
    return drug_dict, drug_smile


def convert2graph(drug_smile):
    """
    :param drug_smile: list
    :return: smile_graph {} 键值对为 simle: graph
    """
    # 将smile转化为图结构（内部再转化为独热编码）
    smile_graph = {}
    for smile in drug_smile:
        g = smile_to_graph(smile)
        smile_graph[smile] = g
    return smile_graph


if __name__ == '__main__':
    #drug_dict, drug_smile = load_drug_smile('./data_WS/drug_SMILES_750.csv')
    #print(drug_dict)
    #smile = drug_smile[0: 10]
    #print(smile)
    #smile_graph = convert2graph(smile)
    #a = smile_graph[smile[1]]
    #print(a)
    #print(a[1])
    #print(np.asarray(a[1]).shape)
    # b = np.asarray(a[1])
    #print(b[:, 0])
    #print(b[0])
    smile_graph = convert2graph(['C[N+]1(CCC2=CC(=C(C=C2C1CC3=CC(=C(C=C3)OC)OC)OC)OC)CCC(=O)OCCCCCOC(=O)CC[N+]4(CCC5=CC(=C(C=C5C4CC6=CC(=C(C=C6)OC)OC)OC)OC)C', 'CC1CCC2CC(C(=CC=CC=CC(CC(C(=O)C(C(C(=CC(C(=O)CC(OC(=O)C3CCCCN3C(=O)C(=O)C1(O2)O)C(C)CC4CCC(C(C4)OC)OCCO)C)C)O)OC)C)C)C)OC','CCC1C=C(C(CC=CC=C(C(=O)OC(CC=C(C=C(C1OC2C(C(C(C(O2)(C)C)OC(=O)C(C)C)O)O)C)C)C(C)O)COC3C(C(C(C(O3)C)OC(=O)C4=C(C(=C(C(=C4O)Cl)O)Cl)CC)O)OC)O)C','CC(CN1CCN(CCN(CCN(CC1)CC(=O)[O-])CC(=O)[O-])CC(=O)[O-])O.[Gd+3]','CC1=CN=C(C(=C1OC)C)CS(=O)C2=NC3=C(N2)C=C(C=C3)OC','C1CC(C1)(C(=O)O)C(=O)O.[NH2-].[NH2-].[Pt+2]','CC(C)C(C)C=CC(C)C1CCC2C1(CCCC2=CC=C3CC(CC(C3=C)O)O)C','C1=CC(=CC=C1C(=O)NCCC(=O)O)N=NC2=CC(=C(C=C2)O)C(=O)O','CC1CCCC2(C(O2)CC(NC(=O)CC(C(C(=O)C(C1O)C)(C)C)O)C(=CC3=CSC(=N3)C)C)C'])
    #print(type(smile_graph))
    #print(smile_graph['O.O.O.[OH-].[O--].[O--].[O--].[O--].[O--].[O--].[O--].[O--].[Na+].[Na+].[Fe+3].[Fe+3].[Fe+3].[Fe+3].[Fe+3].OC[C@H]1O[C@@](CO)(O[C@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)[C@@H](O)[C@@H]1O'])
    #print(type(smile_graph['C[N+]1(CCC2=CC(=C(C=C2C1CC3=CC(=C(C=C3)OC)OC)OC)OC)CCC(=O)OCCCCCOC(=O)CC[N+]4(CCC5=CC(=C(C=C5C4CC6=CC(=C(C=C6)OC)OC)OC)OC)C']))
    print(np.asarray(smile_graph['C[N+]1(CCC2=CC(=C(C=C2C1CC3=CC(=C(C=C3)OC)OC)OC)OC)CCC(=O)OCCCCCOC(=O)CC[N+]4(CCC5=CC(=C(C=C5C4CC6=CC(=C(C=C6)OC)OC)OC)OC)C'][1]).shape)
    print(np.array(smile_graph['CC1CCC2CC(C(=CC=CC=CC(CC(C(=O)C(C(C(=CC(C(=O)CC(OC(=O)C3CCCCN3C(=O)C(=O)C1(O2)O)C(C)CC4CCC(C(C4)OC)OCCO)C)C)O)OC)C)C)C)OC'][1]).shape)
    print(np.array(smile_graph['CCC1C=C(C(CC=CC=C(C(=O)OC(CC=C(C=C(C1OC2C(C(C(C(O2)(C)C)OC(=O)C(C)C)O)O)C)C)C(C)O)COC3C(C(C(C(O3)C)OC(=O)C4=C(C(=C(C(=C4O)Cl)O)Cl)CC)O)OC)O)C'][1]).shape)
    print(np.array(smile_graph['CC1CCCC2(C(O2)CC(NC(=O)CC(C(C(=O)C(C1O)C)(C)C)O)C(=CC3=CSC(=N3)C)C)C'][1]).shape)
    pass
