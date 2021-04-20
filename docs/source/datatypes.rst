Type Arithmetic
===============

Apolloscape's datatypes are represented as trees of depth-3, with each level respectively storing the section, subsection and file type of the data.

Datatypes can be grouped by merging their tree representations.
We define the following operations:

Union
-----

Adding a type to another is done by merging the branches.

.. mermaid::

    flowchart TD
        subgraph C["A ∪ B"]
            C_root[root]
            C_root --> C_S1([seg])
            C_root --> C_S2([ins])
            C_S1 --> C_SS11([ColorImage])
            C_S1 --> C_SS12([Label])
            C_SS11 --> C_FT111([jpg])
            C_SS12 --> C_FT121([bin.png])
            C_S2 --> C_SS21([Label])
            C_S2 --> C_SS22([Depth])
            C_SS21 --> C_FT211([bin.png])
            C_SS22 --> C_FT221([png])
        end
        subgraph B[B]
            B_root[root]
            B_root --> B_S1([ins])
            B_S1 --> B_SS11([Depth])
            B_SS11 --> B_FT111([png])
        end
        subgraph A[A]
            A_root[root]
            A_root --> A_S1([seg])
            A_root --> A_S2([ins])
            A_S1 --> A_SS11([ColorImage])
            A_S1 --> A_SS12([Label])
            A_SS11 --> A_FT111([jpg])
            A_SS12 --> A_FT112([bin.png])
            A_S2 --> A_SS21([Label])
            A_SS21 --> A_FT211([bin.png])
        end

        classDef ANode fill:#b4d273
        classDef BNode fill:#6c99bb
        classDef BothNode fill:#9e86c8

        class A_S1,A_SS11,A_SS12,A_SS21 ANode
        class A_FT111,A_FT112,A_FT211 ANode
        class B_SS11,B_FT111 BNode
        class A_root,A_S2,B_root,B_S1,C_root,C_S2 BothNode
        class C_S1,C_SS11,C_SS12,C_SS21,C_FT111,C_FT121,C_FT211 ANode
        class C_SS22,C_FT221 BNode


Substraction
------------

Removing a type is done by removing its branches from the other composite type while keeping the nodes that still have other children.

.. mermaid::

    flowchart TD
        subgraph C["A − B"]
            C_root[root]
            C_root --> C_S1([ins])
            C_S1 --> C_SS11([Label])
            C_S1 --> C_SS12([Depth])
            C_SS11 --> C_FT111([bin.png])
            C_SS12 --> C_FT121([png])
        end
        subgraph B[B]
            B_root[root]
            B_root --> B_S1([seg])
            B_root --> B_S2([ins])
            B_S1 --> B_SS11([Label])
            B_SS11 --> B_FT111([bin.png])
            B_S2 --> B_SS21([Label])
            B_SS21 --> B_FT211([instanceIds.png])
        end
        subgraph A[A]
            A_root[root]
            A_root --> A_S1([seg])
            A_root --> A_S2([ins])
            A_S1 --> A_SS11([Label])
            A_SS11 --> A_FT111([bin.png])
            A_S2 --> A_SS21([Label])
            A_S2 --> A_SS22([Depth])
            A_SS21 --> A_FT211([bin.png])
            A_SS21 --> A_FT212([instanceIds.png])
            A_SS22 --> A_FT221([png])
        end

        classDef ANode fill:#b4d273
        classDef BNode fill:#6c99bb
        classDef BothNode fill:#9e86c8
        classDef KeepNode fill:#b05279

        class A_SS22,A_FT211,A_FT221,C_SS12,C_FT111,C_FT121 ANode
        class A_S1,A_SS11,A_FT111,A_FT212,B_S1,B_SS11,B_FT111,B_FT211 BothNode
        class A_root,A_S2,A_SS21,B_root,B_S2,B_SS21,C_root,C_S1,C_SS11 KeepNode


Intersection
------------

Intersection is done by keeping the common branches. 

.. mermaid::

    flowchart TD
        subgraph C["A ∩ B"]
            C_root[root]
            C_root --> C_S1([ins])
            C_S1 --> C_SS11([Label])
            C_SS11 --> C_FT111([bin.png])
        end
        subgraph B[B]
            B_root[root]
            B_root --> B_S1([seg])
            B_root --> B_S2([ins])
            B_S1 --> B_SS11([ColorImage])
            B_SS11 --> B_FT111([jpg])
            B_S2 --> B_SS21([Label])
            B_S2 --> B_SS22([ColorImage])
            B_SS21 --> B_FT211([bin.png])
            B_SS22 --> B_FT221([jpg])
        end
        subgraph A[A]
            A_root[root]
            A_root --> A_S1([seg])
            A_root --> A_S2([ins])
            A_S1 --> A_SS11([Label])
            A_SS11 --> A_FT111([bin.png])
            A_S2 --> A_SS21([Label])
            A_SS21 --> A_FT211([bin.png])
            A_SS21 --> A_FT212([instanceIds.png])
        end

        classDef ANode fill:#b4d273
        classDef BNode fill:#6c99bb
        classDef BothNode fill:#9e86c8

        class A_S1,A_SS11,A_FT111,A_FT212 ANode
        class B_S1,B_SS11,B_SS22,B_FT111,B_FT221 BNode
        class A_root,A_S2,A_SS21,A_FT211,B_root,B_S2,B_SS21,B_FT211 BothNode
        class C_root,C_S1,C_SS11,C_FT111 BothNode


Sequence Arithmetic
===================

Sequence arithmetic is the same as Type arithmetic, except sequence, subsequence and file type are respectively replaced by road, record and camera.
