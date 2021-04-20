===
API
===

.. mermaid::
    :caption: Package structure
    
    graph TD

        subgraph apolloscope
            subgraph scene_parsing
                visualisation([visualisation])
                pytorch([pytorch])
                subgraph path
                    regex([regex])
                    register([register])
                end
                subgraph datatype
                    identifier([identifier])
                    color([color])
                    depth([depth])
                    instance([instance])
                    semantic([semantic])
                end
            end
        end


.. toctree::
    :caption: Automatic list

    api/modules
