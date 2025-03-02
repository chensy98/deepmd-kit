// SPDX-License-Identifier: LGPL-3.0-or-later
#pragma once

#include <paddle/include/paddle_inference_api.h>

#include "DeepPot.h"

namespace deepmd {
/**
 * @brief Paddle implementation for Deep Potential.
 **/
class DeepPotPD : public DeepPotBackend {
 public:
  /**
   * @brief DP constructor without initialization.
   **/
  DeepPotPD();
  virtual ~DeepPotPD();
  /**
   * @brief DP constructor with initialization.
   * @param[in] model The name of the frozen model file.
   * @param[in] gpu_rank The GPU rank. Default is 0.
   * @param[in] file_content The content of the model file. If it is not empty,
   *DP will read from the string instead of the file.
   **/
  DeepPotPD(const std::string& model,
            const int& gpu_rank = 0,
            const std::string& file_content = "");
  /**
   * @brief Initialize the DP.
   * @param[in] model The name of the frozen model file.
   * @param[in] gpu_rank The GPU rank. Default is 0.
   * @param[in] file_content The content of the model file. If it is not empty,
   *DP will read from the string instead of the file.
   **/
  void init(const std::string& model,
            const int& gpu_rank = 0,
            const std::string& file_content = "");

 private:
  /**
   * @brief Evaluate the energy, force, virial, atomic energy, and atomic virial
   *by using this DP.
   * @param[out] ener The system energy.
   * @param[out] force The force on each atom.
   * @param[out] virial The virial.
   * @param[out] atom_energy The atomic energy.
   * @param[out] atom_virial The atomic virial.
   * @param[in] coord The coordinates of atoms. The array should be of size
   *nframes x natoms x 3.
   * @param[in] atype The atom types. The list should contain natoms ints.
   * @param[in] box The cell of the region. The array should be of size nframes
   *x 9.
   * @param[in] fparam The frame parameter. The array can be of size :
   * nframes x dim_fparam.
   * dim_fparam. Then all frames are assumed to be provided with the same
   *fparam.
   * @param[in] aparam The atomic parameter The array can be of size :
   * nframes x natoms x dim_aparam.
   * natoms x dim_aparam. Then all frames are assumed to be provided with the
   *same aparam.
   * @param[in] atomic Whether to compute the atomic energy and virial.
   **/
  template <typename VALUETYPE, typename ENERGYVTYPE>
  void compute(ENERGYVTYPE& ener,
               std::vector<VALUETYPE>& force,
               std::vector<VALUETYPE>& virial,
               std::vector<VALUETYPE>& atom_energy,
               std::vector<VALUETYPE>& atom_virial,
               const std::vector<VALUETYPE>& coord,
               const std::vector<int>& atype,
               const std::vector<VALUETYPE>& box,
               const std::vector<VALUETYPE>& fparam,
               const std::vector<VALUETYPE>& aparam,
               const bool atomic);
  /**
   * @brief Evaluate the energy, force, virial, atomic energy, and atomic virial
   *by using this DP.
   * @param[out] ener The system energy.
   * @param[out] force The force on each atom.
   * @param[out] virial The virial.
   * @param[out] atom_energy The atomic energy.
   * @param[out] atom_virial The atomic virial.
   * @param[in] coord The coordinates of atoms. The array should be of size
   *nframes x natoms x 3.
   * @param[in] atype The atom types. The list should contain natoms ints.
   * @param[in] box The cell of the region. The array should be of size nframes
   *x 9.
   * @param[in] nghost The number of ghost atoms.
   * @param[in] lmp_list The input neighbour list.
   * @param[in] ago Update the internal neighbour list if ago is 0.
   * @param[in] fparam The frame parameter. The array can be of size :
   * nframes x dim_fparam.
   * dim_fparam. Then all frames are assumed to be provided with the same
   *fparam.
   * @param[in] aparam The atomic parameter The array can be of size :
   * nframes x natoms x dim_aparam.
   * natoms x dim_aparam. Then all frames are assumed to be provided with the
   *same aparam.
   * @param[in] atomic Whether to compute the atomic energy and virial.
   **/
  template <typename VALUETYPE, typename ENERGYVTYPE>
  void compute(ENERGYVTYPE& ener,
               std::vector<VALUETYPE>& force,
               std::vector<VALUETYPE>& virial,
               std::vector<VALUETYPE>& atom_energy,
               std::vector<VALUETYPE>& atom_virial,
               const std::vector<VALUETYPE>& coord,
               const std::vector<int>& atype,
               const std::vector<VALUETYPE>& box,
               const int nghost,
               const InputNlist& lmp_list,
               const int& ago,
               const std::vector<VALUETYPE>& fparam,
               const std::vector<VALUETYPE>& aparam,
               const bool atomic);
  /**
   * @brief Evaluate the energy, force, and virial with the mixed type
   *by using this DP.
   * @param[out] ener The system energy.
   * @param[out] force The force on each atom.
   * @param[out] virial The virial.
   * @param[in] nframes The number of frames.
   * @param[in] coord The coordinates of atoms. The array should be of size
   *nframes x natoms x 3.
   * @param[in] atype The atom types. The array should be of size nframes x
   *natoms.
   * @param[in] box The cell of the region. The array should be of size nframes
   *x 9.
   * @param[in] fparam The frame parameter. The array can be of size :
   * nframes x dim_fparam.
   * dim_fparam. Then all frames are assumed to be provided with the same
   *fparam.
   * @param[in] aparam The atomic parameter The array can be of size :
   * nframes x natoms x dim_aparam.
   * natoms x dim_aparam. Then all frames are assumed to be provided with the
   *same aparam.
   * @param[in] atomic Whether to compute the atomic energy and virial.
   **/
  template <typename VALUETYPE, typename ENERGYVTYPE>
  void compute_mixed_type(ENERGYVTYPE& ener,
                          std::vector<VALUETYPE>& force,
                          std::vector<VALUETYPE>& virial,
                          const int& nframes,
                          const std::vector<VALUETYPE>& coord,
                          const std::vector<int>& atype,
                          const std::vector<VALUETYPE>& box,
                          const std::vector<VALUETYPE>& fparam,
                          const std::vector<VALUETYPE>& aparam,
                          const bool atomic);
  /**
   * @brief Evaluate the energy, force, and virial with the mixed type
   *by using this DP.
   * @param[out] ener The system energy.
   * @param[out] force The force on each atom.
   * @param[out] virial The virial.
   * @param[out] atom_energy The atomic energy.
   * @param[out] atom_virial The atomic virial.
   * @param[in] nframes The number of frames.
   * @param[in] coord The coordinates of atoms. The array should be of size
   *nframes x natoms x 3.
   * @param[in] atype The atom types. The array should be of size nframes x
   *natoms.
   * @param[in] box The cell of the region. The array should be of size nframes
   *x 9.
   * @param[in] fparam The frame parameter. The array can be of size :
   * nframes x dim_fparam.
   * dim_fparam. Then all frames are assumed to be provided with the same
   *fparam.
   * @param[in] aparam The atomic parameter The array can be of size :
   * nframes x natoms x dim_aparam.
   * natoms x dim_aparam. Then all frames are assumed to be provided with the
   *same aparam.
   * @param[in] atomic Whether to compute the atomic energy and virial.
   **/
  template <typename VALUETYPE, typename ENERGYVTYPE>
  void compute_mixed_type(ENERGYVTYPE& ener,
                          std::vector<VALUETYPE>& force,
                          std::vector<VALUETYPE>& virial,
                          std::vector<VALUETYPE>& atom_energy,
                          std::vector<VALUETYPE>& atom_virial,
                          const int& nframes,
                          const std::vector<VALUETYPE>& coord,
                          const std::vector<int>& atype,
                          const std::vector<VALUETYPE>& box,
                          const std::vector<VALUETYPE>& fparam,
                          const std::vector<VALUETYPE>& aparam,
                          const bool atomic);

 public:
  /**
   * @brief Get the cutoff radius.
   * @return The cutoff radius.
   **/
  double cutoff() const {
    assert(inited);
    return rcut;
  };
  /**
   * @brief Get the number of types.
   * @return The number of types.
   **/
  int numb_types() const {
    assert(inited);
    return ntypes;
  };
  /**
   * @brief Get the number of types with spin.
   * @return The number of types with spin.
   **/
  int numb_types_spin() const {
    assert(inited);
    return ntypes_spin;
  };
  /**
   * @brief Get the dimension of the frame parameter.
   * @return The dimension of the frame parameter.
   **/
  int dim_fparam() const {
    assert(inited);
    return dfparam;
  };
  /**
   * @brief Get the dimension of the atomic parameter.
   * @return The dimension of the atomic parameter.
   **/
  int dim_aparam() const {
    assert(inited);
    return daparam;
  };
  /**
   * @brief Get the type map (element name of the atom types) of this model.
   * @param[out] type_map The type map of this model.
   **/
  void get_type_map(std::string& type_map);

  /**
   * @brief Get the buffer arraay of this model.
   * @param[in] buffer_name Buffer name.
   * @param[out] buffer_array Buffer array.
   **/
  template <typename BUFFERTYPE>
  void get_buffer(const std::string& buffer_name,
                  std::vector<BUFFERTYPE>& buffer_array);

  /**
   * @brief Get the buffer scalar of this model.
   * @param[in] buffer_name Buffer name.
   * @param[out] buffer_scalar Buffer scalar.
   **/
  template <typename BUFFERTYPE>
  void get_buffer(const std::string& buffer_name, BUFFERTYPE& buffer_scalar);

  /**
   * @brief Get whether the atom dimension of aparam is nall instead of fparam.
   * @param[out] aparam_nall whether the atom dimension of aparam is nall
   *instead of fparam.
   **/
  bool is_aparam_nall() const {
    assert(inited);
    return aparam_nall;
  };

  /**
   * @brief Print the shape of given tensor.
   * @param[in] x Tensor x.
   **/
  void print_shape(const paddle_infer::Tensor& x) const {
    std::vector<int> x_shape = x.shape();
    std::string shape_str = "[";
    for (int i = 0, n = x_shape.size(); i < n; ++i) {
      if (i > 0) {
        shape_str += ", ";
      }
      shape_str += std::to_string(x_shape[i]);
    }
    shape_str += "]";
    std::cout << shape_str;
  };

  /**
   * @brief Compute the number of elements in a tensor.
   * @param[in] x Tensor x.
   **/
  int numel(const paddle_infer::Tensor& x) const {
    // TODO: There might be a overflow problem here for multiply int numbers.
    int ret = 1;
    std::vector<int> x_shape = x.shape();
    for (std::size_t i = 0, n = x_shape.size(); i < n; ++i) {
      ret *= x_shape[i];
    }
    return ret;
  };

  // forward to template class
  void computew(std::vector<double>& ener,
                std::vector<double>& force,
                std::vector<double>& virial,
                std::vector<double>& atom_energy,
                std::vector<double>& atom_virial,
                const std::vector<double>& coord,
                const std::vector<int>& atype,
                const std::vector<double>& box,
                const std::vector<double>& fparam,
                const std::vector<double>& aparam,
                const bool atomic);
  void computew(std::vector<double>& ener,
                std::vector<float>& force,
                std::vector<float>& virial,
                std::vector<float>& atom_energy,
                std::vector<float>& atom_virial,
                const std::vector<float>& coord,
                const std::vector<int>& atype,
                const std::vector<float>& box,
                const std::vector<float>& fparam,
                const std::vector<float>& aparam,
                const bool atomic);
  void computew(std::vector<double>& ener,
                std::vector<double>& force,
                std::vector<double>& virial,
                std::vector<double>& atom_energy,
                std::vector<double>& atom_virial,
                const std::vector<double>& coord,
                const std::vector<int>& atype,
                const std::vector<double>& box,
                const int nghost,
                const InputNlist& inlist,
                const int& ago,
                const std::vector<double>& fparam,
                const std::vector<double>& aparam,
                const bool atomic);
  void computew(std::vector<double>& ener,
                std::vector<float>& force,
                std::vector<float>& virial,
                std::vector<float>& atom_energy,
                std::vector<float>& atom_virial,
                const std::vector<float>& coord,
                const std::vector<int>& atype,
                const std::vector<float>& box,
                const int nghost,
                const InputNlist& inlist,
                const int& ago,
                const std::vector<float>& fparam,
                const std::vector<float>& aparam,
                const bool atomic);
  void computew_mixed_type(std::vector<double>& ener,
                           std::vector<double>& force,
                           std::vector<double>& virial,
                           std::vector<double>& atom_energy,
                           std::vector<double>& atom_virial,
                           const int& nframes,
                           const std::vector<double>& coord,
                           const std::vector<int>& atype,
                           const std::vector<double>& box,
                           const std::vector<double>& fparam,
                           const std::vector<double>& aparam,
                           const bool atomic);
  void computew_mixed_type(std::vector<double>& ener,
                           std::vector<float>& force,
                           std::vector<float>& virial,
                           std::vector<float>& atom_energy,
                           std::vector<float>& atom_virial,
                           const int& nframes,
                           const std::vector<float>& coord,
                           const std::vector<int>& atype,
                           const std::vector<float>& box,
                           const std::vector<float>& fparam,
                           const std::vector<float>& aparam,
                           const bool atomic);

 private:
  int num_intra_nthreads, num_inter_nthreads;
  bool inited;
  int ntypes;
  int ntypes_spin;
  int dfparam;
  int daparam;
  int aparam_nall;
  // copy neighbor list info from host
  // config & predictor for model.forward
  std::shared_ptr<paddle_infer::Config> config;
  std::shared_ptr<paddle_infer::Predictor> predictor;
  // config & predictor for model.forward_lower
  std::shared_ptr<paddle_infer::Config> config_fl;
  std::shared_ptr<paddle_infer::Predictor> predictor_fl;

  double rcut;
  NeighborListData nlist_data;
  int max_num_neighbors;
  int gpu_id;
  // use int instead bool for problems may meets with vector<bool>
  int do_message_passing;  // 1:dpa2 model 0:others
  bool gpu_enabled;
  std::unique_ptr<paddle_infer::Tensor> firstneigh_tensor;
  // std::unordered_map<std::string, paddle::Tensor> comm_dict; # Not used yet
};

}  // namespace deepmd
